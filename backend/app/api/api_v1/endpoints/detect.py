import asyncio
import subprocess
import base64
import json
import httpx
import dns.resolver
import logging
import threading
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime
from app.db.session import get_db
from app.db.models import User, DnsRecord, DnsZone, DetectionLog, SystemLog, DetectionStatus
from app.api.deps import get_current_user, require_permission
from app.core.config import settings

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Browser pool for Playwright reuse
_browser_pool = []
_browser_lock = threading.Lock()
_max_browsers = 3


def get_browser():
    """Get a browser from pool or create new one"""
    with _browser_lock:
        if _browser_pool:
            browser = _browser_pool.pop()
            logger.info(f"[PLAYWRIGHT] Reusing browser from pool, pool size: {len(_browser_pool)}")
            return browser

    logger.info(f"[PLAYWRIGHT] Creating new browser")
    from playwright.sync_api import sync_playwright
    pw = sync_playwright().start()
    browser = pw.chromium.launch(headless=True)
    return pw, browser


def return_browser(pw, browser):
    """Return browser to pool"""
    with _browser_lock:
        if len(_browser_pool) < _max_browsers:
            _browser_pool.append((pw, browser))
            logger.info(f"[PLAYWRIGHT] Returned browser to pool, pool size: {len(_browser_pool)}")
        else:
            logger.info(f"[PLAYWRIGHT] Pool full, closing browser")
            browser.close()
            pw.stop()

router = APIRouter(prefix="/detect", tags=["detect"])


async def resolve_cname_to_ips(cname: str, db: AsyncSession) -> list[str]:
    """
    Resolve CNAME to IPs:
    1. First look up in local database
    2. If not found, use DNS query to resolve A records
    """
    cname_clean = cname.rstrip(".")

    # 1. Try to find A records in local database for the CNAME target
    result = await db.execute(
        select(DnsRecord).where(
            DnsRecord.name.like(f"%{cname_clean}%"),
            DnsRecord.type == "A",
            DnsRecord.rdata.isnot(None)
        )
    )
    local_records = result.scalars().all()
    if local_records:
        ips = [r.rdata for r in local_records if r.rdata]
        if ips:
            return ips

    # 2. Use dnspython to resolve A records externally
    try:
        resolver = dns.resolver.Resolver()
        resolver.timeout = 5
        resolver.lifetime = 5
        answers = resolver.resolve(cname_clean, 'A')
        ips = [str(rdata) for rdata in answers]
        if ips:
            return ips
    except dns.resolver.NXDOMAIN:
        pass
    except dns.resolver.NoAnswer:
        pass
    except Exception as e:
        pass

    # 3. Try AAAA (IPv6)
    try:
        resolver = dns.resolver.Resolver()
        resolver.timeout = 5
        resolver.lifetime = 5
        answers = resolver.resolve(cname_clean, 'AAAA')
        ips = [str(rdata) for rdata in answers]
        if ips:
            return ips
    except:
        pass

    return []


async def ping_host(ip: str, timeout: int = 5) -> dict:
    """Ping a host and return result - uses thread pool to avoid async subprocess issues"""
    logger.info(f"[PING] Starting ping to {ip} with timeout {timeout}s")

    def sync_ping():
        """Synchronous ping using subprocess.run"""
        try:
            # Windows ping: -n count, -w timeout in ms
            result = subprocess.run(
                ["ping", "-n", "1", "-w", str(timeout * 1000), ip],
                capture_output=True,
                timeout=timeout + 5,  # Slightly longer than ping timeout
            )

            # Try GBK first (Windows default), then UTF-8
            stdout_text = ""
            stderr_text = ""
            try:
                stdout_text = result.stdout.decode("gbk", errors="ignore")
            except:
                stdout_text = result.stdout.decode("utf-8", errors="ignore")

            try:
                stderr_text = result.stderr.decode("gbk", errors="ignore")
            except:
                stderr_text = result.stderr.decode("utf-8", errors="ignore")

            output = stdout_text + stderr_text

            # Check for success: returncode 0 OR "TTL=" in output
            success = result.returncode == 0 or "TTL=" in output.upper()

            return {
                "status": "success" if success else "failed",
                "output": output,
                "returncode": result.returncode,
            }
        except subprocess.TimeoutExpired:
            return {
                "status": "error",
                "output": "Ping timeout expired",
                "returncode": -1,
            }
        except FileNotFoundError:
            return {
                "status": "error",
                "output": "ping command not found",
                "returncode": -1,
            }
        except Exception as e:
            return {
                "status": "error",
                "output": f"{type(e).__name__}: {e}",
                "returncode": -1,
            }

    try:
        # Run sync ping in thread pool
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, sync_ping)
        logger.info(f"[PING] {ip} - status={result['status']}, returncode={result['returncode']}")
        logger.info(f"[PING] Output: {result.get('output', '')[:200]}")
        return result
    except Exception as e:
        logger.error(f"[PING] Exception in executor: {type(e).__name__}: {e}")
        return {
            "status": "error",
            "output": f"{type(e).__name__}: {e}",
            "returncode": -1,
        }


async def curl_url(url: str, timeout: int = 10) -> dict:
    """Curl a URL using httpx to check if it's accessible - tries http and https"""
    logger.info(f"[CURL] Checking URL: {url}")

    # Strip existing scheme if present
    clean_url = url
    for scheme in ["http://", "https://"]:
        if url.lower().startswith(scheme):
            clean_url = url[len(scheme):]
            break

    # Try http first, then https
    for scheme in ["http", "https"]:
        full_url = f"{scheme}://{clean_url}"
        try:
            logger.info(f"[CURL] Trying {full_url}...")
            async with httpx.AsyncClient(
                timeout=timeout,
                follow_redirects=True,
                verify=False,
                headers={"User-Agent": "DNS-Health-Check/1.0"}
            ) as client:
                response = await client.get(full_url)
                http_code = str(response.status_code)
                logger.info(f"[CURL] {full_url} returned {http_code}")

                return {
                    "status": "success" if response.status_code in [200, 301, 302, 304] else "failed",
                    "http_code": http_code,
                    "output": f"Status: {response.status_code}, Length: {len(response.content)}",
                    "url": full_url,
                }
        except httpx.TimeoutException:
            logger.warning(f"[CURL] Timeout for {full_url}")
            continue
        except Exception as e:
            logger.warning(f"[CURL] Failed for {full_url}: {type(e).__name__}: {e}")
            continue

    # All attempts failed
    return {
        "status": "failed",
        "http_code": "error",
        "output": "Could not connect with http or https",
        "url": clean_url,
    }


def capture_screenshot(url: str, timeout: int = 15) -> dict:
    """Capture screenshot using playwright with browser pool"""
    from app.core.config import get_detection_config
    import os
    from datetime import datetime

    logger.info(f"[PLAYWRIGHT] Starting screenshot capture for {url}")

    # Get snapshot save path from config
    snapshot_path = get_detection_config("snapshot_save_path", "./snapshots")
    save_to_file = get_detection_config("save_screenshot_to_file", "true").lower() == "true"

    # Get timeout from config (convert seconds to ms)
    screenshot_timeout = int(get_detection_config("detection_timeout", "15")) * 1000
    logger.info(f"[PLAYWRIGHT] Timeout: {screenshot_timeout}ms, Save to file: {save_to_file}, Path: {snapshot_path}")

    # Strip existing scheme if present
    clean_url = url
    for scheme in ["http://", "https://"]:
        if url.lower().startswith(scheme):
            clean_url = url[len(scheme):]
            break
    logger.info(f"[PLAYWRIGHT] Clean URL: {clean_url}")

    pw = None
    browser = None
    try:
        # Get browser from pool
        pool_item = get_browser()
        if isinstance(pool_item, tuple):
            pw, browser = pool_item
        else:
            browser = pool_item

        page = browser.new_page(
            viewport={"width": 1280, "height": 720},
            user_agent="DNS-Health-Check/1.0"
        )

        # Try http first, then https
        final_url = None
        for scheme in ["http", "https"]:
            try:
                full_url = f"{scheme}://{clean_url}"
                logger.info(f"[PLAYWRIGHT] Trying {full_url}...")
                page.goto(full_url, timeout=screenshot_timeout, wait_until="domcontentloaded")
                final_url = full_url
                logger.info(f"[PLAYWRIGHT] Successfully loaded {full_url}")
                break
            except Exception as e:
                logger.warning(f"[PLAYWRIGHT] Failed to load {full_url}: {e}")
                continue

        if not final_url:
            logger.warning(f"[PLAYWRIGHT] Could not load any URL for {url}")
            page.close()
            return_browser(pw, browser)
            return {
                "status": "error",
                "screenshot": None,
                "output": "Could not load page with http or https",
            }

        # Take screenshot BEFORE closing the page
        screenshot_bytes = page.screenshot(full_page=False)
        page.close()

        # Return browser to pool
        return_browser(pw, browser)
        pw = None
        browser = None

        screenshot_base64 = base64.b64encode(screenshot_bytes).decode()

        # Save to file system if enabled
        saved_file_path = None
        if save_to_file and snapshot_path:
            try:
                os.makedirs(snapshot_path, exist_ok=True)
                # Generate filename: domain_timestamp.png
                timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
                safe_url = url.replace(".", "_").replace(":", "_").replace("/", "_")
                filename = f"{safe_url}_{timestamp}.png"
                file_path = os.path.join(snapshot_path, filename)

                with open(file_path, "wb") as f:
                    f.write(screenshot_bytes)

                saved_file_path = file_path
                logger.info(f"[PLAYWRIGHT] Screenshot saved to: {file_path}")
            except Exception as e:
                logger.error(f"[PLAYWRIGHT] Failed to save screenshot to file: {e}")

        output_msg = f"Screenshot captured for {final_url}"
        if saved_file_path:
            output_msg += f", saved to: {saved_file_path}"

        return {
            "status": "success",
            "screenshot": screenshot_base64,
            "output": output_msg,
            "file_path": saved_file_path,
        }
    except Exception as e:
        logger.error(f"[PLAYWRIGHT] Exception: {type(e).__name__}: {e}")
        # Make sure to clean up on error
        if browser:
            try:
                return_browser(pw, browser)
            except:
                pass
        return {
            "status": "error",
            "screenshot": None,
            "output": f"{type(e).__name__}: {e}",
        }


async def ai_check_page(screenshot_base64: str, url: str) -> dict:
    """Use OpenAI to check if page is normal"""
    from app.core.config import get_ai_config, settings as app_settings

    logger.info(f"[AI_CHECK] Starting AI analysis for {url}")

    # Get AI config - first from cache (DB), then fallback to .env
    api_key = get_ai_config("openai_api_key") or app_settings.openai_api_key
    base_url = get_ai_config("openai_base_url") or app_settings.openai_base_url
    model = get_ai_config("openai_model") or app_settings.openai_model
    prompt_template = get_ai_config("ai_prompt_template", "Analyze this screenshot of {url} and determine if the page is normal (accessible and showing expected content) or abnormal (error page, 404, 500, SSL error, etc.). Return JSON: {{\"status\": \"normal\" or \"abnormal\", \"reason\": \"brief explanation\"}}")
    ai_enabled = get_ai_config("ai_enabled", "true").lower() == "true"

    logger.info(f"[AI_CHECK] Config - enabled={ai_enabled}, model={model}, base_url={base_url[:30]}...")

    if not ai_enabled:
        logger.info(f"[AI_CHECK] AI detection is disabled")
        return {
            "status": "error",
            "result": "AI detection is disabled",
        }

    if not api_key:
        logger.warning(f"[AI_CHECK] OpenAI API key not configured")
        return {
            "status": "error",
            "result": "OpenAI API key not configured",
        }

    try:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=api_key, base_url=base_url)

        # Format prompt with URL
        prompt = prompt_template.replace("{url}", url)
        logger.info(f"[AI_CHECK] Sending request to AI model {model}")

        response = await client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt,
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{screenshot_base64}"},
                        },
                    ],
                }
            ],
        )

        # Qwen model might put reasoning in reasoning field instead of content
        message = response.choices[0].message
        result_text = message.content or message.reasoning or ""
        logger.info(f"[AI_CHECK] Received response - content: {str(message.content)[:200]}, reasoning: {str(message.reasoning)[:200]}")
        logger.info(f"[AI_CHECK] Full response: {message}")

        if not result_text:
            logger.warning(f"[AI_CHECK] Empty response from AI")
            return {
                "status": "error",
                "result": "Empty response from AI",
            }

        # Try to parse JSON from response
        parsed = None
        try:
            # Extract JSON from response
            import re
            json_match = re.search(r"\{.*\}", result_text, re.DOTALL)
            logger.info(f"[AI_CHECK] JSON match found: {json_match is not None}")
            if json_match:
                matched_str = json_match.group()
                logger.info(f"[AI_CHECK] Matched string: {matched_str[:200]}")
                parsed = json.loads(matched_str)
                logger.info(f"[AI_CHECK] Parsed JSON: {parsed}, type: {type(parsed)}")

                # Handle different response formats
                if isinstance(parsed, dict):
                    return {
                        "status": "success",
                        "result": parsed.get("status") or parsed.get("result") or parsed.get("Status") or "unknown",
                        "reason": parsed.get("reason") or parsed.get("message") or parsed.get("Reason") or result_text,
                    }
                elif isinstance(parsed, str):
                    return {
                        "status": "success",
                        "result": parsed.lower() if parsed else "unknown",
                        "reason": result_text,
                    }
        except json.JSONDecodeError as e:
            logger.warning(f"[AI_CHECK] JSON decode error: {e}, raw text: {result_text[:200]}")
        except KeyError as e:
            logger.error(f"[AI_CHECK] KeyError during parsing: {e}, parsed: {parsed}, text: {result_text[:200]}")
        except Exception as e:
            logger.warning(f"[AI_CHECK] Failed to parse response: {type(e).__name__}: {e}")

        # If no valid JSON found, analyze response text directly
        result_text_lower = result_text.lower()
        if "normal" in result_text_lower and "abnormal" not in result_text_lower:
            final_result = "normal"
        elif "abnormal" in result_text_lower:
            final_result = "abnormal"
        else:
            final_result = "unknown"

        logger.info(f"[AI_CHECK] Fallback result: {final_result}")
        return {
            "status": "success",
            "result": final_result,
            "reason": result_text[:200] if len(result_text) > 200 else result_text,
        }
    except Exception as e:
        logger.error(f"[AI_CHECK] Exception: {type(e).__name__}: {e}")
        return {
            "status": "error",
            "result": f"{type(e).__name__}: {e}",
        }


async def detect_record_task(record_id: int, db: AsyncSession):
    """Background task to detect a single record"""
    from app.core.config import get_detection_config

    # Get record
    result = await db.execute(select(DnsRecord).where(DnsRecord.id == record_id))
    record = result.scalar_one_or_none()
    if not record:
        logger.warning(f"[DETECT] Record {record_id} not found")
        return

    logger.info(f"[DETECT] Starting detection for record {record_id}: {record.name} ({record.type})")
    record_type = record.type.upper()

    # Get detection settings
    ping_enabled = get_detection_config("default_ping_enabled", "true").lower() == "true"
    curl_enabled = get_detection_config("default_curl_enabled", "true").lower() == "true"
    playwright_enabled = get_detection_config("default_playwright_enabled", "true").lower() == "true"
    ai_check_enabled = get_detection_config("default_ai_check_enabled", "true").lower() == "true"

    logger.info(f"[DETECT] Settings - ping={ping_enabled}, curl={curl_enabled}, playwright={playwright_enabled}, ai={ai_check_enabled}")
    logger.info(f"[DETECT] Raw config values: ping={get_detection_config('default_ping_enabled')}, curl={get_detection_config('default_curl_enabled')}, playwright={get_detection_config('default_playwright_enabled')}, ai={get_detection_config('default_ai_check_enabled')}")

    # 1. Ping detection (for A records with IP, and CNAME records resolved to IP)
    ping_ips = []

    if record_type == "A" and record.rdata:
        # Direct A record - use the IP in rdata
        ping_ips = [record.rdata]
        logger.info(f"[DETECT] A record, using IP: {ping_ips}")
    elif record_type == "CNAME" and record.rdata:
        # CNAME record - resolve to IPs
        cname_target = record.rdata.rstrip(".")
        logger.info(f"[DETECT] CNAME record, resolving: {cname_target}")
        ping_ips = await resolve_cname_to_ips(cname_target, db)
        logger.info(f"[DETECT] CNAME resolved to IPs: {ping_ips}")

    # Perform ping detection for resolved IPs (if enabled)
    if ping_enabled and ping_ips:
        logger.info(f"[DETECT] Starting ping detection for IPs: {ping_ips}")
        record.ping_status = DetectionStatus.RUNNING.value
        await db.commit()

        # Get timeout from config (default 15 seconds)
        ping_timeout = int(get_detection_config("detection_timeout", "15"))
        logger.info(f"[DETECT] Ping timeout: {ping_timeout}s")

        ping_results = []
        for ip in ping_ips:
            logger.info(f"[DETECT] Pinging {ip}...")
            ping_result = await ping_host(ip, timeout=ping_timeout)
            logger.info(f"[DETECT] Ping result for {ip}: {ping_result}")
            ping_results.append(f"{ip}: {ping_result['status']} (output: {ping_result.get('output', '')[:100]})")

        # If any IP responds, mark as success
        overall_success = any("success" in r for r in ping_results)
        record.ping_status = DetectionStatus.SUCCESS.value if overall_success else DetectionStatus.FAILED.value
        record.ping_result = "; ".join(ping_results)
        record.ping_time = datetime.utcnow()

        logger.info(f"[DETECT] Ping detection completed: {record.ping_status} - {record.ping_result}")

        # Log detection
        log = DetectionLog(
            record_id=record.id,
            detection_type="ping",
            status=record.ping_status,
            result=record.ping_result,
        )
        db.add(log)
        await db.commit()
    elif record_type in ["A", "CNAME"]:
        # No IP found to ping
        record.ping_status = DetectionStatus.FAILED.value
        record.ping_result = "No IP address found to ping"
        await db.commit()

    # 2. Curl detection
    if curl_enabled and record_type in ["A", "CNAME"] and record.name:
        record.curl_status = DetectionStatus.RUNNING.value
        await db.commit()

        # Get timeout from config (default 15 seconds)
        curl_timeout = int(get_detection_config("detection_timeout", "15"))

        # Build URL (remove trailing dot)
        domain = record.name.rstrip(".")
        curl_result = await curl_url(f"http://{domain}", timeout=curl_timeout)
        record.curl_status = DetectionStatus.SUCCESS.value if curl_result["status"] == "success" else DetectionStatus.FAILED.value
        record.curl_result = f"HTTP {curl_result.get('http_code', 'N/A')}: {curl_result.get('output', '')}"
        record.curl_time = datetime.utcnow()

        log = DetectionLog(
            record_id=record.id,
            detection_type="curl",
            status=record.curl_status,
            result=record.curl_result,
        )
        db.add(log)
        await db.commit()

    # 3. Playwright screenshot
    if playwright_enabled and record_type in ["A", "CNAME"] and record.name:
        record.playwright_status = DetectionStatus.RUNNING.value
        await db.commit()

        domain = record.name.rstrip(".")
        # Run sync playwright in thread pool
        loop = asyncio.get_event_loop()
        screenshot_result = await loop.run_in_executor(None, capture_screenshot, f"http://{domain}")

        if screenshot_result["status"] == "success":
            record.playwright_status = DetectionStatus.SUCCESS.value
            record.playwright_screenshot = screenshot_result["screenshot"]
            record.playwright_result = screenshot_result["output"]
        else:
            record.playwright_status = DetectionStatus.FAILED.value
            record.playwright_result = screenshot_result["output"]

        record.playwright_time = datetime.utcnow()

        log = DetectionLog(
            record_id=record.id,
            detection_type="playwright",
            status=record.playwright_status,
            result=record.playwright_result,
            screenshot=record.playwright_screenshot,
        )
        db.add(log)
        await db.commit()

        # 4. AI check (only if screenshot was successful and AI is enabled)
        if ai_check_enabled and screenshot_result.get("screenshot"):
            record.ai_check_status = DetectionStatus.RUNNING.value
            await db.commit()

            try:
                ai_result = await ai_check_page(screenshot_result["screenshot"], domain)
                logger.info(f"[DETECT] AI result: {ai_result}")
                record.ai_check_status = DetectionStatus.SUCCESS.value if ai_result.get("status") == "success" else DetectionStatus.FAILED.value
                record.ai_check_result = str(ai_result.get("result", "unknown")) + ": " + str(ai_result.get("reason", ""))
            except Exception as e:
                logger.error(f"[DETECT] AI check exception: {type(e).__name__}: {e}")
                record.ai_check_status = DetectionStatus.FAILED.value
                record.ai_check_result = f"Error: {type(e).__name__}: {e}"

            record.ai_check_time = datetime.utcnow()

            log = DetectionLog(
                record_id=record.id,
                detection_type="ai",
                status=record.ai_check_status,
                result=record.ai_check_result,
            )
            db.add(log)
            await db.commit()

    # For MX records - check mail server
    elif record_type == "MX" and record.rdata:
        # MX records have format: priority mailserver
        parts = record.rdata.split()
        if len(parts) >= 2:
            mailserver = parts[1].rstrip(".")
            # Try to curl the mailserver
            record.curl_status = DetectionStatus.RUNNING.value
            await db.commit()

            # Use config timeout
            curl_timeout = int(get_detection_config("detection_timeout", "15"))
            curl_result = await curl_url(f"http://{mailserver}", timeout=curl_timeout)
            record.curl_status = DetectionStatus.SUCCESS.value if curl_result["status"] == "success" else DetectionStatus.FAILED.value
            record.curl_result = f"MX {mailserver}: {curl_result.get('http_code', 'N/A')}"
            record.curl_time = datetime.utcnow()

            log = DetectionLog(
                record_id=record.id,
                detection_type="curl",
                status=record.curl_status,
                result=record.curl_result,
            )
            db.add(log)
            await db.commit()

    # For NS records - check nameserver
    elif record_type == "NS" and record.rdata:
        # Check if NS server is reachable
        ns_server = record.rdata.rstrip(".")
        record.curl_status = DetectionStatus.RUNNING.value
        await db.commit()

        # Use config timeout
        curl_timeout = int(get_detection_config("detection_timeout", "15"))
        curl_result = await curl_url(f"http://{ns_server}", timeout=curl_timeout)
        record.curl_status = DetectionStatus.SUCCESS.value if curl_result["status"] == "success" else DetectionStatus.FAILED.value
        record.curl_result = f"NS {ns_server}: {curl_result.get('http_code', 'N/A')}"
        record.curl_time = datetime.utcnow()

        log = DetectionLog(
            record_id=record.id,
            detection_type="curl",
            status=record.curl_status,
            result=record.curl_result,
        )
        db.add(log)
        await db.commit()


@router.post("/record/{record_id}")
async def detect_record(
    record_id: int,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("detect:execute")),
):
    """Detect a single DNS record"""
    result = await db.execute(select(DnsRecord).where(DnsRecord.id == record_id))
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Record not found",
        )

    logger.info(f"[API] User {current_user.username} started detection for record {record_id}: {record.name} ({record.type})")

    background_tasks.add_task(detect_record_task, record_id, db)

    log = SystemLog(
        action="detect_record",
        level="info",
        user_id=current_user.id,
        details=f"Started detection for record {record_id}: {record.name}",
    )
    db.add(log)
    await db.commit()

    return {"message": "Detection started", "record_id": record_id}


@router.post("/zone/{zone_id}")
async def detect_zone(
    zone_id: int,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("detect:execute")),
):
    """Detect all records in a zone"""
    result = await db.execute(
        select(DnsRecord).where(DnsRecord.zone_id == zone_id)
    )
    records = result.scalars().all()

    if not records:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No records found for this zone",
        )

    logger.info(f"[API] User {current_user.username} started detection for zone {zone_id}, {len(records)} records")

    for record in records:
        background_tasks.add_task(detect_record_task, record.id, db)

    log = SystemLog(
        action="detect_zone",
        level="info",
        user_id=current_user.id,
        details=f"Started detection for zone {zone_id}, {len(records)} records",
    )
    db.add(log)
    await db.commit()

    return {"message": "Detection started", "zone_id": zone_id, "records_count": len(records)}


@router.post("/all")
async def detect_all(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("detect:execute")),
):
    """Detect all DNS records"""
    result = await db.execute(select(DnsRecord))
    records = result.scalars().all()

    if not records:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No records to detect",
        )

    logger.info(f"[API] User {current_user.username} started detection for all {len(records)} records")

    for record in records:
        background_tasks.add_task(detect_record_task, record.id, db)

    log = SystemLog(
        action="detect_all",
        level="info",
        user_id=current_user.id,
        details=f"Started detection for all {len(records)} records",
    )
    db.add(log)
    await db.commit()

    return {"message": "Detection started", "total_records": len(records)}
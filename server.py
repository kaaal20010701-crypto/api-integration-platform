from flask import Flask, request, jsonify, send_from_directory, Response
from flask_cors import CORS
import requests
import base64
import json
import os
import io

try:
    from PIL import Image
    _HAS_PIL = True
except ImportError:
    _HAS_PIL = False

app = Flask(__name__)
CORS(app)
ROOT = os.path.dirname(os.path.abspath(__file__))

try:
    from dotenv import load_dotenv

    load_dotenv(os.path.join(ROOT, ".env"))
except ImportError:
    pass

# 百度云：从环境变量或项目根目录 .env 读取（勿将 .env 提交到公开仓库）
BAIDU_ESSAY_API_KEY = os.environ.get("BAIDU_ESSAY_API_KEY", "").strip()
BAIDU_ESSAY_SECRET_KEY = os.environ.get("BAIDU_ESSAY_SECRET_KEY", "").strip()
BAIDU_TOKEN_URL = "https://aip.baidubce.com/oauth/2.0/token"
BAIDU_CORRECT_EDU_CREATE_URL = "https://aip.baidubce.com/rest/2.0/ocr/v1/correct_edu/create_task"
BAIDU_CORRECT_EDU_GET_RESULT_URL = "https://aip.baidubce.com/rest/2.0/ocr/v1/correct_edu/get_result"
BAIDU_HANDWRITING_COMPOSITION_CREATE_URL = "https://aip.baidubce.com/rest/2.0/ocr/v1/handwriting_composition/create_task"
BAIDU_HANDWRITING_COMPOSITION_GET_RESULT_URL = "https://aip.baidubce.com/rest/2.0/ocr/v1/handwriting_composition/get_result"
BAIDU_IDCARD_URL = "https://aip.baidubce.com/rest/2.0/ocr/v1/idcard"
BAIDU_PADDLE_VL_PARSER_CREATE_URL = "https://aip.baidubce.com/rest/2.0/brain/online/v2/paddle-vl-parser/task"
BAIDU_PADDLE_VL_PARSER_QUERY_URL = "https://aip.baidubce.com/rest/2.0/brain/online/v2/paddle-vl-parser/task/query"
BAIDU_DOC_ANALYSIS_URL = "https://aip.baidubce.com/rest/2.0/ocr/v1/doc_analysis"
BAIDU_DOC_ANALYSIS_OFFICE_URL = "https://aip.baidubce.com/rest/2.0/ocr/v1/doc_analysis_office"
BAIDU_OCR_ACCURATE_URL = "https://aip.baidubce.com/rest/2.0/ocr/v1/accurate"
BAIDU_PAPER_CUT_EDU_URL = "https://aip.baidubce.com/rest/2.0/ocr/v1/paper_cut_edu"
BAIDU_BANKCARD_URL = "https://aip.baidubce.com/rest/2.0/ocr/v1/bankcard"


def _parse_json_response(resp, name="接口"):
    """解析 HTTP 响应为 JSON；若返回非 JSON（如 HTML 错误页）则抛出明确异常。"""
    text = resp.text if resp.text is not None else ""
    try:
        return json.loads(text)
    except Exception as e:
        snippet = text[:300] if text else "(空响应)"
        raise ValueError(
            f"{name}返回了非 JSON 内容（可能是错误页），请检查网络或稍后重试。响应片段: {snippet!r}"
        ) from e


def _get_baidu_access_token():
    if not BAIDU_ESSAY_API_KEY or not BAIDU_ESSAY_SECRET_KEY:
        raise RuntimeError(
            "未配置百度云凭证：请设置环境变量 BAIDU_ESSAY_API_KEY 与 BAIDU_ESSAY_SECRET_KEY，"
            "或在项目根目录复制 .env.example 为 .env 并填入密钥。"
        )
    resp = requests.get(
        BAIDU_TOKEN_URL,
        params={
            "grant_type": "client_credentials",
            "client_id": BAIDU_ESSAY_API_KEY,
            "client_secret": BAIDU_ESSAY_SECRET_KEY,
        },
        timeout=10,
    )
    resp.raise_for_status()
    data = _parse_json_response(resp, "百度 Token")
    if "access_token" not in data:
        raise RuntimeError("Baidu token response missing access_token: " + str(data))
    return data["access_token"]


def _send_html_no_cache(rel_path):
    """发送 HTML 文件并禁止缓存与 304，确保浏览器拿到最新内容。"""
    file_path = os.path.join(ROOT, rel_path)
    if not os.path.isfile(file_path):
        return None
    with open(file_path, "rb") as f:
        body = f.read()
    resp = Response(body, mimetype="text/html; charset=utf-8")
    resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    resp.headers["Pragma"] = "no-cache"
    resp.headers["Expires"] = "0"
    return resp


@app.route('/')
def index():
    """提供前端入口，避免用 file:// 打开导致的 fetch 失败。"""
    return _send_html_no_cache("index.html") or send_from_directory(ROOT, "index.html")


@app.route('/<path:path>')
def serve_static(path):
    """提供 css、demos 等静态文件。"""
    if path.endswith(".html") or path.startswith("demos/"):
        r = _send_html_no_cache(path)
        if r is not None:
            return r
    return send_from_directory(ROOT, path)


@app.route('/api/demo/baidu_correct_edu', methods=['POST'])
def demo_baidu_correct_edu():
    """百度云智能作业批改：端到端批改（异步）或仅题目切分（同步）。"""
    try:
        only_split = request.form.get("only_split", "false").lower() in ("true", "1", "yes")
        body = {"only_split": only_split}

        if request.files and "file" in request.files and request.files["file"].filename:
            f = request.files["file"]
            raw = f.read()
            if _HAS_PIL:
                try:
                    img = Image.open(io.BytesIO(raw)).copy()
                    if img.mode in ("RGBA", "P", "LA"):
                        img = img.convert("RGB")
                    buf = io.BytesIO()
                    img.save(buf, format="JPEG", quality=92)
                    raw = buf.getvalue()
                except Exception:
                    pass
            b64 = base64.b64encode(raw).decode("utf-8")
            body["image"] = b64
        elif request.form.get("url"):
            body["url"] = request.form.get("url").strip()
        else:
            return jsonify({"error": "请上传图片文件或填写图片 URL"}), 400

        token = _get_baidu_access_token()
        create_resp = requests.post(
            f"{BAIDU_CORRECT_EDU_CREATE_URL}?access_token={token}",
            json=body,
            headers={"Content-Type": "application/json"},
            timeout=15,
        )
        create_resp.raise_for_status()
        create_data = _parse_json_response(create_resp, "百度 correct_edu create_task")
        ec = create_data.get("error_code")
        if ec is not None and ec not in (0, "0"):
            return jsonify(create_data), 400
        task_id = (create_data.get("result") or {}).get("task_id")
        # 仅题目切分：同步返回，可能无 task_id，直接返回 create 结果
        if not task_id:
            return jsonify(create_data)

        # 端到端批改：轮询 get_result，建议 5～10 秒
        import time
        max_polls = 30
        poll_interval = 6
        for _ in range(max_polls):
            time.sleep(poll_interval)
            result_resp = requests.post(
                f"{BAIDU_CORRECT_EDU_GET_RESULT_URL}?access_token={token}",
                json={"task_id": task_id},
                headers={"Content-Type": "application/json"},
                timeout=15,
            )
            result_resp.raise_for_status()
            result_data = _parse_json_response(result_resp, "百度 correct_edu get_result")
            err_code = result_data.get("error_code")
            err_msg = (result_data.get("error_msg") or "").lower()
            # 处理中：继续轮询，不要当错误返回
            if err_code in (1, "1") and ("pending" in err_msg or not err_msg):
                continue
            if err_code is not None and err_code not in (0, "0"):
                return jsonify(result_data), 400
            if result_data.get("isAllFinished") is True:
                return jsonify(result_data)
            # 未完成也继续轮询
        return jsonify({"error": "轮询超时", "task_id": task_id}), 408
    except requests.RequestException as e:
        return jsonify({"error": "请求百度接口失败", "detail": str(e)}), 502
    except ValueError as e:
        return jsonify({"error": str(e)}), 502
    except Exception as e:
        err_msg = str(e)
        if "JSON" in err_msg or "property name" in err_msg:
            return jsonify({"error": "百度接口返回了非 JSON 内容，请检查网络或稍后重试。"}), 502
        return jsonify({"error": err_msg}), 500


@app.route('/api/demo/baidu_handwriting_composition', methods=['POST'])
def demo_baidu_handwriting_composition():
    """百度云手写作文识别（多模态）：异步接口，create_task → 轮询 get_result。"""
    try:
        body = {}
        recognize_granularity = request.form.get("recognize_granularity", "").strip().lower()
        if recognize_granularity and recognize_granularity in ("none", "line", "word"):
            body["recognize_granularity"] = recognize_granularity
        pdf_file_num = request.form.get("pdf_file_num", "").strip()
        if pdf_file_num and pdf_file_num.isdigit():
            body["pdf_file_num"] = pdf_file_num

        if request.files and "file" in request.files and request.files["file"].filename:
            f = request.files["file"]
            raw = f.read()
            fname = (f.filename or "").lower()
            if fname.endswith(".pdf"):
                body["pdf_file"] = base64.b64encode(raw).decode("utf-8")
            else:
                if _HAS_PIL:
                    try:
                        img = Image.open(io.BytesIO(raw)).copy()
                        if img.mode in ("RGBA", "P", "LA"):
                            img = img.convert("RGB")
                        buf = io.BytesIO()
                        img.save(buf, format="JPEG", quality=92)
                        raw = buf.getvalue()
                    except Exception:
                        pass
                body["image"] = base64.b64encode(raw).decode("utf-8")
        elif request.form.get("url"):
            body["url"] = request.form.get("url").strip()
        else:
            return jsonify({"error": "请上传图片/PDF 文件或填写图片 URL"}), 400

        token = _get_baidu_access_token()
        create_resp = requests.post(
            f"{BAIDU_HANDWRITING_COMPOSITION_CREATE_URL}?access_token={token}",
            json=body,
            headers={"Content-Type": "application/json"},
            timeout=15,
        )
        create_resp.raise_for_status()
        create_data = _parse_json_response(create_resp, "百度 handwriting_composition create_task")
        ec = create_data.get("error_code")
        if ec is not None and ec not in (0, "0"):
            return jsonify(create_data), 400
        task_id = (create_data.get("result") or {}).get("task_id")
        if not task_id:
            return jsonify(create_data)

        import time
        max_polls = 30
        poll_interval = 6
        for _ in range(max_polls):
            time.sleep(poll_interval)
            result_resp = requests.post(
                f"{BAIDU_HANDWRITING_COMPOSITION_GET_RESULT_URL}?access_token={token}",
                json={"task_id": task_id},
                headers={"Content-Type": "application/json"},
                timeout=15,
            )
            result_resp.raise_for_status()
            result_data = _parse_json_response(result_resp, "百度 handwriting_composition get_result")
            err_code = result_data.get("error_code")
            err_msg = (result_data.get("error_msg") or "").lower()
            if err_code in (1, "1") and ("pending" in err_msg or "processing" in err_msg or not err_msg):
                continue
            if err_code is not None and err_code not in (0, "0"):
                return jsonify(result_data), 400
            res = result_data.get("result") or {}
            status = (res.get("status") or "").lower()
            if status in ("success",):
                return jsonify(result_data)
            if status == "failed":
                return jsonify(result_data), 400
        return jsonify({"error": "轮询超时", "task_id": task_id}), 408
    except requests.RequestException as e:
        return jsonify({"error": "请求百度接口失败", "detail": str(e)}), 502
    except ValueError as e:
        return jsonify({"error": str(e)}), 502
    except Exception as e:
        err_msg = str(e)
        if "JSON" in err_msg or "property name" in err_msg:
            return jsonify({"error": "百度接口返回了非 JSON 内容，请检查网络或稍后重试。"}), 502
        return jsonify({"error": err_msg}), 500


@app.route('/api/demo/baidu_idcard', methods=['POST'])
def demo_baidu_idcard():
    """百度云身份证识别：同步接口，支持 image/url，id_card_side 必选，可选 detect_* 等。"""
    try:
        body = {}
        if request.files and "file" in request.files and request.files["file"].filename:
            f = request.files["file"]
            raw = f.read()
            if _HAS_PIL:
                try:
                    img = Image.open(io.BytesIO(raw)).copy()
                    if img.mode in ("RGBA", "P", "LA"):
                        img = img.convert("RGB")
                    buf = io.BytesIO()
                    img.save(buf, format="JPEG", quality=92)
                    raw = buf.getvalue()
                except Exception:
                    pass
            body["image"] = base64.b64encode(raw).decode("utf-8")
        elif request.form.get("url"):
            body["url"] = request.form.get("url").strip()
        else:
            return jsonify({"error": "请上传图片文件或填写图片 URL"}), 400

        id_card_side = request.form.get("id_card_side", "front").strip().lower()
        if id_card_side not in ("front", "back"):
            id_card_side = "front"
        body["id_card_side"] = id_card_side

        for key in ("detect_ps", "detect_risk", "detect_quality", "detect_photo", "detect_card", "detect_direction", "detect_screenshot"):
            val = request.form.get(key, "false").lower() in ("true", "1", "yes")
            body[key] = "true" if val else "false"

        token = _get_baidu_access_token()
        resp = requests.post(
            f"{BAIDU_IDCARD_URL}?access_token={token}",
            data=body,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=15,
        )
        resp.raise_for_status()
        data = _parse_json_response(resp, "百度 idcard")
        ec = data.get("error_code")
        if ec is not None and ec not in (0, "0"):
            return jsonify(data), 400
        return jsonify(data)
    except requests.RequestException as e:
        return jsonify({"error": "请求百度接口失败", "detail": str(e)}), 502
    except ValueError as e:
        return jsonify({"error": str(e)}), 502
    except Exception as e:
        err_msg = str(e)
        if "JSON" in err_msg or "property name" in err_msg:
            return jsonify({"error": "百度接口返回了非 JSON 内容，请检查网络或稍后重试。"}), 502
        return jsonify({"error": err_msg}), 500


@app.route('/api/demo/baidu_bankcard', methods=['POST'])
def demo_baidu_bankcard():
    """百度云银行卡识别：同步接口，支持 image/url，可选 location、detect_quality。"""
    try:
        body = {}
        if request.files and "file" in request.files and request.files["file"].filename:
            f = request.files["file"]
            raw = f.read()
            if _HAS_PIL:
                try:
                    img = Image.open(io.BytesIO(raw)).copy()
                    if img.mode in ("RGBA", "P", "LA"):
                        img = img.convert("RGB")
                    buf = io.BytesIO()
                    img.save(buf, format="JPEG", quality=92)
                    raw = buf.getvalue()
                except Exception:
                    pass
            body["image"] = base64.b64encode(raw).decode("utf-8")
        elif request.form.get("url"):
            body["url"] = request.form.get("url").strip()
        else:
            return jsonify({"error": "请上传图片文件或填写图片 URL"}), 400

        location = request.form.get("location", "false").lower() in ("true", "1", "yes")
        body["location"] = "true" if location else "false"

        detect_quality = request.form.get("detect_quality", "false").lower() in ("true", "1", "yes")
        body["detect_quality"] = "true" if detect_quality else "false"

        token = _get_baidu_access_token()
        resp = requests.post(
            f"{BAIDU_BANKCARD_URL}?access_token={token}",
            data=body,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=15,
        )
        resp.raise_for_status()
        data = _parse_json_response(resp, "百度 bankcard")
        ec = data.get("error_code")
        if ec is not None and ec not in (0, "0"):
            return jsonify(data), 400
        return jsonify(data)
    except requests.RequestException as e:
        return jsonify({"error": "请求百度接口失败", "detail": str(e)}), 502
    except ValueError as e:
        return jsonify({"error": str(e)}), 502
    except Exception as e:
        err_msg = str(e)
        if "JSON" in err_msg or "property name" in err_msg:
            return jsonify({"error": "百度接口返回了非 JSON 内容，请检查网络或稍后重试。"}), 502
        return jsonify({"error": err_msg}), 500


@app.route('/api/demo/baidu_paddle_vl_parser', methods=['POST'])
def demo_baidu_paddle_vl_parser():
    """百度云文档解析（PaddleOCR-VL）：异步接口，提交任务后轮询获取结果，支持 PDF、图片等文档。"""
    import time
    try:
        data = {}
        if request.files and "file" in request.files and request.files["file"].filename:
            f = request.files["file"]
            raw = f.read()
            fname = (f.filename or "document.pdf").strip()
            data["file_data"] = base64.b64encode(raw).decode("utf-8")
        elif request.form.get("file_url"):
            data["file_url"] = request.form.get("file_url").strip()
            fname = request.form.get("file_name", "").strip() or "document.pdf"
        else:
            return jsonify({"error": "请上传文档文件或填写 file_url"}), 400

        data["file_name"] = fname if fname else "document.pdf"

        for key, default in [
            ("analysis_chart", "false"),
            ("merge_tables", "false"),
            ("relevel_titles", "false"),
            ("recognize_seal", "false"),
            ("return_span_boxes", "false"),
        ]:
            val = request.form.get(key, default).lower() in ("true", "1", "yes")
            data[key] = "true" if val else "false"

        token = _get_baidu_access_token()
        create_resp = requests.post(
            f"{BAIDU_PADDLE_VL_PARSER_CREATE_URL}?access_token={token}",
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=30,
        )
        create_resp.raise_for_status()
        create_data = _parse_json_response(create_resp, "百度 paddle-vl-parser create_task")
        ec = create_data.get("error_code")
        if ec is not None and ec not in (0, "0"):
            return jsonify(create_data), 400
        task_id = (create_data.get("result") or {}).get("task_id")
        if not task_id:
            return jsonify(create_data)

        max_polls = 60
        poll_interval = 6
        for _ in range(max_polls):
            time.sleep(poll_interval)
            query_data = {"task_id": task_id}
            result_resp = requests.post(
                f"{BAIDU_PADDLE_VL_PARSER_QUERY_URL}?access_token={token}",
                data=query_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=15,
            )
            result_resp.raise_for_status()
            result_data = _parse_json_response(result_resp, "百度 paddle-vl-parser task/query")
            err_code = result_data.get("error_code")
            if err_code is not None and err_code not in (0, "0"):
                return jsonify(result_data), 400
            res = result_data.get("result") or {}
            status = (res.get("status") or "").lower()
            if status == "success":
                parse_result_url = res.get("parse_result_url")
                markdown_url = res.get("markdown_url")
                parse_content = None
                if parse_result_url:
                    try:
                        parse_resp = requests.get(parse_result_url, timeout=30)
                        parse_resp.raise_for_status()
                        parse_content = json.loads(parse_resp.text or "{}")
                    except Exception as e:
                        result_data["_parse_fetch_error"] = str(e)
                result_data["parse_content"] = parse_content
                result_data["markdown_url"] = markdown_url
                return jsonify(result_data)
            if status == "failed":
                return jsonify(result_data), 400
        return jsonify({"error": "轮询超时", "task_id": task_id}), 408
    except requests.RequestException as e:
        return jsonify({"error": "请求百度接口失败", "detail": str(e)}), 502
    except ValueError as e:
        return jsonify({"error": str(e)}), 502
    except Exception as e:
        err_msg = str(e)
        if "JSON" in err_msg or "property name" in err_msg:
            return jsonify({"error": "百度接口返回了非 JSON 内容，请检查网络或稍后重试。"}), 502
        return jsonify({"error": err_msg}), 500


@app.route('/api/demo/baidu_doc_analysis', methods=['POST'])
def demo_baidu_doc_analysis():
    """百度云试卷分析与识别：同步接口，支持 image/url/pdf_file，可选 language_type、result_type、版面分析、公式识别等。"""
    try:
        body = {}
        if request.files and "file" in request.files and request.files["file"].filename:
            f = request.files["file"]
            raw = f.read()
            fname = (f.filename or "").lower()
            if fname.endswith(".pdf"):
                body["pdf_file"] = base64.b64encode(raw).decode("utf-8")
            else:
                if _HAS_PIL:
                    try:
                        img = Image.open(io.BytesIO(raw)).copy()
                        if img.mode in ("RGBA", "P", "LA"):
                            img = img.convert("RGB")
                        buf = io.BytesIO()
                        img.save(buf, format="JPEG", quality=92)
                        raw = buf.getvalue()
                    except Exception:
                        pass
                body["image"] = base64.b64encode(raw).decode("utf-8")
        elif request.form.get("url"):
            body["url"] = request.form.get("url").strip()
        else:
            return jsonify({"error": "请上传图片/PDF 文件或填写图片 URL"}), 400

        pdf_file_num = request.form.get("pdf_file_num", "").strip()
        if pdf_file_num and pdf_file_num.isdigit():
            body["pdf_file_num"] = pdf_file_num

        for key, default in [
            ("language_type", "CHN_ENG"),
            ("result_type", "big"),
        ]:
            val = request.form.get(key, default).strip()
            if val:
                body[key] = val

        for key in (
            "detect_direction", "line_probability", "disp_line_poly",
            "layout_analysis", "recg_formula", "recg_long_division",
            "disp_underline_analysis", "recg_alter",
        ):
            val = request.form.get(key, "false").lower() in ("true", "1", "yes")
            body[key] = "true" if val else "false"

        words_type = request.form.get("words_type", "").strip()
        if words_type in ("handwring_only", "handprint_mix"):
            body["words_type"] = words_type

        token = _get_baidu_access_token()
        resp = requests.post(
            f"{BAIDU_DOC_ANALYSIS_URL}?access_token={token}",
            data=body,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=30,
        )
        resp.raise_for_status()
        data = _parse_json_response(resp, "百度 doc_analysis")
        ec = data.get("error_code")
        if ec is not None and ec not in (0, "0"):
            return jsonify(data), 400
        return jsonify(data)
    except requests.RequestException as e:
        return jsonify({"error": "请求百度接口失败", "detail": str(e)}), 502
    except ValueError as e:
        return jsonify({"error": str(e)}), 502
    except Exception as e:
        err_msg = str(e)
        if "JSON" in err_msg or "property name" in err_msg:
            return jsonify({"error": "百度接口返回了非 JSON 内容，请检查网络或稍后重试。"}), 502
        return jsonify({"error": err_msg}), 500


@app.route('/api/demo/baidu_paper_cut_edu', methods=['POST'])
def demo_baidu_paper_cut_edu():
    """百度云试卷切题识别：同步接口，支持 image/url/pdf_file，题目自动切分与结构化识别。"""
    try:
        body = {}
        if request.files and "file" in request.files and request.files["file"].filename:
            f = request.files["file"]
            raw = f.read()
            fname = (f.filename or "").lower()
            if fname.endswith(".pdf"):
                body["pdf_file"] = base64.b64encode(raw).decode("utf-8")
            else:
                if _HAS_PIL:
                    try:
                        img = Image.open(io.BytesIO(raw)).copy()
                        if img.mode in ("RGBA", "P", "LA"):
                            img = img.convert("RGB")
                        buf = io.BytesIO()
                        img.save(buf, format="JPEG", quality=92)
                        raw = buf.getvalue()
                    except Exception:
                        pass
                body["image"] = base64.b64encode(raw).decode("utf-8")
        elif request.form.get("url"):
            body["url"] = request.form.get("url").strip()
        else:
            return jsonify({"error": "请上传图片/PDF 文件或填写图片 URL"}), 400

        pdf_file_num = request.form.get("pdf_file_num", "").strip()
        if pdf_file_num and pdf_file_num.isdigit():
            body["pdf_file_num"] = pdf_file_num

        language_type = request.form.get("language_type", "").strip()
        if language_type in ("CHN_ENG", "ENG"):
            body["language_type"] = language_type

        words_type = request.form.get("words_type", "").strip()
        if words_type in ("handprint_mix", "handwring_only"):
            body["words_type"] = words_type

        for key in ("detect_direction", "splice_text", "enhance", "only_split"):
            val = request.form.get(key, "false").lower() in ("true", "1", "yes")
            body[key] = "true" if val else "false"

        token = _get_baidu_access_token()
        resp = requests.post(
            f"{BAIDU_PAPER_CUT_EDU_URL}?access_token={token}",
            data=body,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=30,
        )
        resp.raise_for_status()
        data = _parse_json_response(resp, "百度 paper_cut_edu")
        ec = data.get("error_code")
        if ec is not None and ec not in (0, "0"):
            return jsonify(data), 400
        return jsonify(data)
    except requests.RequestException as e:
        return jsonify({"error": "请求百度接口失败", "detail": str(e)}), 502
    except ValueError as e:
        return jsonify({"error": str(e)}), 502
    except Exception as e:
        err_msg = str(e)
        if "JSON" in err_msg or "property name" in err_msg:
            return jsonify({"error": "百度接口返回了非 JSON 内容，请检查网络或稍后重试。"}), 502
        return jsonify({"error": err_msg}), 500


@app.route('/api/demo/baidu_doc_analysis_office', methods=['POST'])
def demo_baidu_doc_analysis_office():
    """百度云办公文档识别：支持 image/url/pdf_file/ofd_file，版面分析、表格/印章/公式/下划线等参数。"""
    try:
        body = {}
        # 文件四选一：image / url / pdf_file / ofd_file
        if request.files and "file" in request.files and request.files["file"].filename:
            f = request.files["file"]
            raw = f.read()
            fname = (f.filename or "").lower()
            if fname.endswith(".pdf"):
                body["pdf_file"] = base64.b64encode(raw).decode("utf-8")
            elif fname.endswith(".ofd"):
                body["ofd_file"] = base64.b64encode(raw).decode("utf-8")
            else:
                if _HAS_PIL:
                    try:
                        img = Image.open(io.BytesIO(raw)).copy()
                        if img.mode in ("RGBA", "P", "LA"):
                            img = img.convert("RGB")
                        buf = io.BytesIO()
                        img.save(buf, format="JPEG", quality=92)
                        raw = buf.getvalue()
                    except Exception:
                        pass
                body["image"] = base64.b64encode(raw).decode("utf-8")
        elif request.form.get("url"):
            body["url"] = request.form.get("url").strip()
        else:
            return jsonify({"error": "请上传图片/PDF/OFD 文件或填写图片 URL"}), 400

        # PDF / OFD 页码
        pdf_file_num = request.form.get("pdf_file_num", "").strip()
        if pdf_file_num and pdf_file_num.isdigit():
            body["pdf_file_num"] = pdf_file_num
        ofd_file_num = request.form.get("ofd_file_num", "").strip()
        if ofd_file_num and ofd_file_num.isdigit():
            body["ofd_file_num"] = ofd_file_num

        # 语言、结果粒度、文字类型
        language_type = request.form.get("language_type", "").strip()
        if language_type:
            body["language_type"] = language_type

        result_type = request.form.get("result_type", "").strip()
        if result_type in ("big", "small"):
            body["result_type"] = result_type

        words_type = request.form.get("words_type", "").strip()
        if words_type in ("handwring_only", "handprint_mix"):
            body["words_type"] = words_type

        # 布尔开关类参数
        for key in (
            "char_probability",
            "detect_direction",
            "line_probability",
            "disp_line_poly",
            "layout_analysis",
            "recg_tables",
            "recog_seal",
            "recg_formula",
            "erase_seal",
            "disp_underline_analysis",
        ):
            val = request.form.get(key)
            if val is not None:
                is_true = str(val).lower() in ("true", "1", "yes", "on")
                body[key] = "true" if is_true else "false"

        token = _get_baidu_access_token()
        resp = requests.post(
            f"{BAIDU_DOC_ANALYSIS_OFFICE_URL}?access_token={token}",
            data=body,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=30,
        )
        resp.raise_for_status()
        data = _parse_json_response(resp, "百度 doc_analysis_office")
        ec = data.get("error_code")
        if ec is not None and ec not in (0, "0"):
            return jsonify(data), 400
        return jsonify(data)
    except requests.RequestException as e:
        return jsonify({"error": "请求百度接口失败", "detail": str(e)}), 502
    except ValueError as e:
        return jsonify({"error": str(e)}), 502
    except Exception as e:
        err_msg = str(e)
        if "JSON" in err_msg or "property name" in err_msg:
            return jsonify({"error": "百度接口返回了非 JSON 内容，请检查网络或稍后重试。"}), 502
        return jsonify({"error": err_msg}), 500


@app.route('/api/demo/baidu_ocr_accurate', methods=['POST'])
def demo_baidu_ocr_accurate():
    """百度云通用文字识别（高精度含位置版）：同步接口，支持 image/url/pdf_file/ofd_file 及多语言与位置/置信度相关参数。"""
    try:
        body = {}
        # 文件三选一：image / pdf_file / ofd_file，或使用 url
        if request.files and "file" in request.files and request.files["file"].filename:
            f = request.files["file"]
            raw = f.read()
            fname = (f.filename or "").lower()
            if fname.endswith(".pdf"):
                body["pdf_file"] = base64.b64encode(raw).decode("utf-8")
            elif fname.endswith(".ofd"):
                body["ofd_file"] = base64.b64encode(raw).decode("utf-8")
            else:
                if _HAS_PIL:
                    try:
                        img = Image.open(io.BytesIO(raw)).copy()
                        if img.mode in ("RGBA", "P", "LA"):
                            img = img.convert("RGB")
                        buf = io.BytesIO()
                        img.save(buf, format="JPEG", quality=92)
                        raw = buf.getvalue()
                    except Exception:
                        pass
                body["image"] = base64.b64encode(raw).decode("utf-8")
        elif request.form.get("url"):
            body["url"] = request.form.get("url").strip()
        else:
            return jsonify({"error": "请上传图片/PDF/OFD 文件或填写图片 URL"}), 400

        # PDF / OFD 页码
        pdf_file_num = request.form.get("pdf_file_num", "").strip()
        if pdf_file_num and pdf_file_num.isdigit():
            body["pdf_file_num"] = pdf_file_num
        ofd_file_num = request.form.get("ofd_file_num", "").strip()
        if ofd_file_num and ofd_file_num.isdigit():
            body["ofd_file_num"] = ofd_file_num

        # 语言与粒度相关参数
        language_type = request.form.get("language_type", "").strip()
        if language_type:
            body["language_type"] = language_type

        eng_granularity = request.form.get("eng_granularity", "").strip()
        if eng_granularity in ("word", "letter"):
            body["eng_granularity"] = eng_granularity

        recognize_granularity = request.form.get("recognize_granularity", "").strip()
        if recognize_granularity in ("big", "small"):
            body["recognize_granularity"] = recognize_granularity

        # 一系列 true/false 开关
        for key in (
            "detect_direction",
            "vertexes_location",
            "paragraph",
            "probability",
            "char_probability",
            "multidirectional_recognize",
        ):
            val = request.form.get(key)
            if val is not None:
                is_true = str(val).lower() in ("true", "1", "yes", "on")
                body[key] = "true" if is_true else "false"

        token = _get_baidu_access_token()
        resp = requests.post(
            f"{BAIDU_OCR_ACCURATE_URL}?access_token={token}",
            data=body,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=30,
        )
        resp.raise_for_status()
        data = _parse_json_response(resp, "百度通用文字识别（高精度含位置版）")
        ec = data.get("error_code")
        if ec is not None and ec not in (0, "0"):
            return jsonify(data), 400
        return jsonify(data)
    except requests.RequestException as e:
        return jsonify({"error": "请求百度接口失败", "detail": str(e)}), 502
    except ValueError as e:
        return jsonify({"error": str(e)}), 502
    except Exception as e:
        err_msg = str(e)
        if "JSON" in err_msg or "property name" in err_msg:
            return jsonify({"error": "百度接口返回了非 JSON 内容，请检查网络或稍后重试。"}), 502
        return jsonify({"error": err_msg}), 500


if __name__ == '__main__':
    # 使用 5001 避免与 macOS AirPlay 占用的 5000 冲突（否则会 403）
    app.run(debug=True, port=5001)

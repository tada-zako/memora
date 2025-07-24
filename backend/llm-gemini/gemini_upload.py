# -*- coding: utf-8 -*-
import base64
import json
import os
import mimetypes

# requests is a third-party library.
# please install it by running: pip install requests
try:
    import requests
except ImportError:
    print("'requests' library not found. Please install it using: pip install requests")
    exit()

# --- 配置加载 ---

def load_config():
    """从config.json加载配置"""
    try:
        with open("config.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# 全局加载配置
config = load_config()
gemini_config = config.get("gemini", {})
proxy_config = config.get("proxy", {})
GEMINI_API_KEY = gemini_config.get("api_key", "YOUR_GEMINI_API_KEY")

# 设置代理
proxies = None
if proxy_config.get("enabled", False):
    proxy_url = proxy_config.get("url")
    if proxy_url:
        proxies = {
            "http": proxy_url,
            "https": proxy_url,
        }
# --- 配置加载结束 ---


# --- 提示词模板库 ---
PROMPT_TEMPLATES = {
    'food': """
    Analyze the food in the image. Identify each food item, estimate its nutritional information, portion size, and assign a meal type. Provide the current timestamp. The final output must be a single JSON object. All string values in the JSON must be in Chinese. Do not add any other text or markdown formatting outside the JSON object.
    The JSON structure should be:
    [
        {
          "meal_type": "早餐/午餐/晚餐/点心/夜宵",
          "timestamp": "YYYY-MM-DDTHH:MM:SSZ",
          "items": [
            {
              "name": "食物名称",
              "calories": 0,
              "protein": 0.0,
              "carbohydrates": 0.0,
              "fat": 0.0,
              "fiber": 0.0,
              "portion_size": 0.0,
              "portion_unit": "克/毫升",
              "nutrition_source": "手动/数据库/应用估算"
            }
          ],
          "total_calories": 0,
          "meal_rating": 0,
          "photo_url": "照片链接"
        }
    ]
    """,
    'location': """
    Analyze the location in the image. Identify the geographical coordinates (latitude, longitude), current weather conditions (temperature in Celsius, description), and classify the location type. The final output must be a single JSON object. All string values in the JSON must be in Chinese. Do not add any other text or markdown formatting outside the JSON object.
    The JSON structure should be:
    {
      "location": {
        "latitude": 0.0,
        "longitude": 0.0,
        "address": "详细地址",
        "location_type": "城市/乡村/自然/室内"
      },
      "weather": {
        "temperature_celsius": 0.0,
        "condition": "晴天/多云/雨天等"
      },
      "description": "详细描述"
    }
    """,
    'exercise': """
    Analyze the image related to physical activity. Identify the type of exercise, estimate physiological metrics like intensity and heart rate, and quantify performance data like distance and elevation. Also, list any equipment used. The final output must be a single JSON object. All string values in the JSON must be in Chinese. Do not add any other text or markdown formatting outside the JSON object.
    The JSON structure should be:
    {
      "exercise": {
        "type": "跑步/骑行等",
        "timestamp": "YYYY-MM-DDTHH:MM:SSZ",
        "duration_minutes": 0,
        "intensity": "低/中/高",
        "avg_heart_rate_bpm": 0,
        "distance_km": 0.0,
        "elevation_gain_meters": 0,
        "equipment": ["设备名称"]
      }
    }
    """,
    'learning': """
    Analyze the image related to a learning session. Identify the learning resources, the topics covered, any potential distractions, and estimate the learning efficiency. The final output must be a single JSON object. All string values in the JSON must be in Chinese. Do not add any other text or markdown formatting outside the JSON object.
    The JSON structure should be:
    {
      "learning_session": {
        "timestamp": "YYYY-MM-DDTHH:MM:SSZ",
        "duration_minutes": 0,
        "topics": ["学习主题"],
        "resources": ["学习资源"],
        "distractions": ["分心因素"],
        "efficiency_rating": 0
      }
    }
    """,
    'sleep': """
    Analyze the image related to sleep (e.g., a sleep tracker summary or bedroom environment). Record sleep data, detailing sleep stages, overall score, potential influencing factors, and morning mood. The final output must be a single JSON object. All string values in the JSON must be in Chinese. Do not add any other text or markdown formatting outside the JSON object.
    The JSON structure should be:
    {
      "sleep_log": {
        "date": "YYYY-MM-DD",
        "time_in_bed_minutes": 0,
        "stages_percentage": {
          "deep": 0.0,
          "light": 0.0,
          "rem": 0.0,
          "awake": 0.0
        },
        "sleep_score": 0,
        "influencing_factors": ["影响因素"],
        "morning_mood": "清爽/昏沉/疲劳"
      }
    }
    """,
    'gaming': """
    Analyze the image from a gaming session. Identify the game, platform, session type, and estimate an enjoyment rating. The final output must be a single JSON object. All string values in the JSON must be in Chinese. Do not add any other text or markdown formatting outside the JSON object.
    The JSON structure should be:
    {
      "gaming_session": {
        "timestamp": "YYYY-MM-DDTHH:MM:SSZ",
        "game_title": "游戏名称",
        "platform": "电脑/主机/手机",
        "session_type": "单人/多人",
        "duration_minutes": 0,
        "enjoyment_rating": 0
      }
    }
    """,
    'programming': """
    Analyze the image from a programming session (e.g., a code screenshot). Identify the project, tech stack, completed tasks, and any new concepts learned. The final output must be a single JSON object. All string values in the JSON must be in Chinese. Do not add any other text or markdown formatting outside the JSON object.
    The JSON structure should be:
    {
      "programming_session": {
        "timestamp": "YYYY-MM-DDTHH:MM:SSZ",
        "project_name": "项目名称",
        "tech_stack": ["技术栈"],
        "tasks_completed": ["完成的任务"],
        "learnings": ["学习内容"]
      }
    }
    """,
    'daily_summary': """
    Based on the provided image which summarizes a day, generate a daily report. Include a daily rating, energy, stress, and mood levels, a gratitude entry, and key takeaways for the day. The final output must be a single JSON object. All string values in the JSON must be in Chinese. Do not add any other text or markdown formatting outside the JSON object.
    The JSON structure should be:
    {
      "daily_summary": {
        "date": "YYYY-MM-DD",
        "overall_rating": 0,
        "energy_level": 0,
        "stress_level": 0,
        "mood": "开心/平静/难过",
        "gratitude_entry": "感恩记录",
        "daily_takeaway": "今日收获"
      }
    }
    """,
    'default': '请详细描述这张图片里的内容，并以合理的JSON格式组织信息。JSON对象内的所有字符串键值都应为中文。'
}

def get_prompt(category):
    """根据类别获取提示词"""
    return PROMPT_TEMPLATES.get(category, PROMPT_TEMPLATES['default'])


# --- 核心工具函数 ---
def run_gemini_analysis(file_path: str, category: str):
    """
    封装后的Gemini图像分析工具。

    :param file_path: 图片文件的完整路径。
    :param category: 图片种类 (例如 'food', 'location', 'exercise' 等)。
    """
    print("--- 开始执行Gemini图像分析 ---")
    
    # 1. 检查API Key
    if GEMINI_API_KEY == "YOUR_GEMINI_API_KEY":
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("!!! 错误: 未配置API Key。请在 config.json 中填入您的密钥!   !!!")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        return

    # 2. 检查文件路径
    if not os.path.exists(file_path):
        print(f"错误: 图片文件未找到于 {file_path}")
        return

    # 3. 获取提示词
    prompt = get_prompt(category)
    print(f"图片种类: '{category}'")

    # 4. 调用API请求
    _send_gemini_request(file_path, prompt)
    print("--- 分析执行结束 ---\n")


def _send_gemini_request(image_path, prompt):
    """
    (内部函数) 负责构造并发送API请求。
    """
    print(f"正在处理图片: {image_path}")
    print(f"使用提示: '{prompt[:100]}...'") # 打印部分提示词以避免刷屏

    # 1. 读取图片并进行Base64编码
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')

    # 2. 获取图片的MIME类型
    mime_type = mimetypes.guess_type(image_path)[0] or 'image/jpeg'
    print(f"检测到图片MIME类型: {mime_type}")

    # 3. 构造请求体
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={GEMINI_API_KEY}"
    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [{
            "parts": [
                {"text": prompt},
                {"inline_data": {"mime_type": mime_type, "data": encoded_string}}
            ]
        }],
        "generationConfig": {
            "response_mime_type": "application/json"
        }
    }

    # 4. 发送POST请求
    try:
        print("正在向Gemini API发送请求...")
        if proxies:
            print(f"使用代理: {proxies.get('https')}")
        response = requests.post(api_url, headers=headers, json=data, timeout=60, proxies=proxies)
        response.raise_for_status()
        
        # 5. 处理响应
        result = response.json()
        handle_json_response(result)

    except requests.exceptions.RequestException as e:
        print(f"请求失败，发生网络错误: {e}")
        if e.response:
            try:
                error_json = e.response.json()
                print(f"响应内容: {json.dumps(error_json, indent=2, ensure_ascii=False)}")
            except json.JSONDecodeError:
                print(f"响应内容: {e.response.text}")
    except Exception as e:
        print(f"发生未知错误: {e}")


def handle_json_response(result):
    """处理JSON响应"""
    if 'candidates' in result and result['candidates']:
        candidate = result['candidates'][0]
        if 'finishReason' in candidate and candidate['finishReason'] == 'SAFETY':
            print("\n--- Gemini的回答被安全策略阻止 ---")
            print("无法生成回复，可能包含不安全内容。")
            print("------------------------------------\n")
        elif 'content' in candidate and 'parts' in candidate['content']:
            try:
                json_text = candidate['content']['parts'][0]['text']
                # 解析JSON并美化打印
                parsed_json = json.loads(json_text)
                print("\n--- Gemini JSON分析结果 ---")
                print(json.dumps(parsed_json, indent=2, ensure_ascii=False))
                print("--------------------------\n")
            except (json.JSONDecodeError, KeyError) as e:
                print("\n--- 解析JSON结果失败 ---")
                print(f"错误: {e}")
                print("API原始响应:")
                print(candidate['content']['parts'][0]['text'])
                print("-----------------------------\n")
        else:
            print_generic_error(result)
    else:
        print_generic_error(result)

def print_generic_error(result):
    """打印通用的错误信息"""
    print("识别失败，未收到有效回复。")
    print("API 原始响应:")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    # ==================================================================
    # --- 工具使用示例 ---
    #
    # 1. 配置要分析的图片路径
    #    请确保路径正确，例如: 'C:/Users/YourUser/Desktop/my_photo.jpg'
    #    或者使用相对路径: 'images/food.jpg'
    image_to_analyze = 'C:/Users/70262/Desktop/breakfast.jpg'
    
    # 2. 定义图片的种类, 从以下选项中选择:
    #    'food', 'location', 'exercise', 'learning', 'sleep', 
    #    'gaming', 'programming', 'daily_summary'
    #    如果类别未在模板库中定义，将使用 'default' 提示词。
    image_category = 'food'
    
    # --- 调用工具 ---
    #    现在只需要传入 file_path 和 category
    run_gemini_analysis(
        file_path=image_to_analyze,
        category=image_category
    )
    # ==================================================================

    # --- 另一个示例：分析一张编程截图 ---
    # run_gemini_analysis(
    #     file_path='path/to/your/code_screenshot.png',
    #     category='programming'
    # ) 
    
    # --- 另一个示例：分析一张风景照 ---
    # run_gemini_analysis(
    #     file_path='path/to/your/landscape.jpg',
    #     category='location'
    # ) 
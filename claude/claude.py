import sublime
import sublime_plugin
import sys 
import os
# sublime text3 不給用 requests
import urllib.request
import json

SETTINGS_PATH = "claude.sublime-settings"
# Ref: https://docs.anthropic.com/en/api/messages
class ClaudeCommand(sublime_plugin.TextCommand):
    
    def get_settings(self):
        return sublime.load_settings(SETTINGS_PATH)

    def run(self, edit):

        # 這裡輸入您的 OpenAI API 密鑰
        api_key = self.get_settings().get("token") 
        # 獲取當前選中的文本
        for region in self.view.sel():
            if not region.empty():
                user_input = self.view.substr(region)
                break
            else:
                sublime.error_message("請選擇要發送的文本。")
                return


        # 發送請求到 OpenAI API
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
            "user-agent":"Hey Judy. Why did you do this?",
        }
        
        
        data = {
            "model": "claude-3-opus-20240229",
            "max_tokens": 1024,
            "messages": [
                {"role": "user", "content": user_input},
                {"role": "assistant","content": "你專門產出指定程式語言的軟體程式碼，重新描述需求並標記註解，以 PHP 為預設的程式語言"}
            ]
        }
        request_data = json.dumps(data).encode('utf-8')

        
        request = urllib.request.Request(url, data=request_data, headers=headers, method="POST")

        try:
            with urllib.request.urlopen(request) as response:
                
                response_data = json.loads(response.read().decode('utf-8'))
                # sublime.error_message(json.dumps(response_data));

                reply = response_data['content'][0]['text'].strip()
                self.view.insert(edit, region.end(), "\n\n" + reply)
        except urllib.error.HTTPError as e:
            sublime.error_message("HTTP Error: " + str(e.code) + "\n" + e.read().decode('utf-8'))
        except urllib.error.URLError as e:
            sublime.error_message("URL Error: " + e.reason)

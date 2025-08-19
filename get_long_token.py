import requests

# Điền thông tin của bạn
APP_ID = "1464644701226823"
APP_SECRET = "67a010c9a18abe7939ca46045c021f19"
SHORT_LIVED_TOKEN = "EAAU0Fisjh0cBPJ9s8mZB0nfYF28Vtp5vWUZCK9ZB4XmNl220ZBTnEmryMeEjrvwZBu5fb795rBytUT4ZAZBL0FwJvzCrfaadBT9CmgV4Bb4pIixEGZA1QcKEA1GedQ7ERWvGW0Nbex3X36vH3BtZAVaT63EPv2qYQagw06claK6XQUrztYOk9XMTFgryKVIOyDsvOMrBZAd4pIji0wgTBrZCJhZBFepPazHULZB01NAT0TwZDZD"

def get_long_lived_token(app_id, app_secret, short_token):
    url = "https://graph.facebook.com/v18.0/oauth/access_token"
    params = {
        "grant_type": "fb_exchange_token",
        "client_id": app_id,
        "client_secret": app_secret,
        "fb_exchange_token": short_token
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        return data.get("access_token")
    else:
        print("Error:", response.json())
        return None

if __name__ == "__main__":
    long_token = get_long_lived_token(APP_ID, APP_SECRET, SHORT_LIVED_TOKEN)
    if long_token:
        print("✅ Long-lived token:")
        print(long_token)
    else:
        print("❌ Không lấy được token")

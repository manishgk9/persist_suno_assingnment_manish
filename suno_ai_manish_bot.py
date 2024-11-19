import telebot
from credential import Token
import time
import requests
import json
bot = telebot.TeleBot(token=Token)


@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_message(
        message.chat.id, "Welcome to Suno AI Song Generator Bot! 🎶")
    send_help(message)


def send_help(message):
    help_text = (
        "To generate a song, just type your prompt! 😎\n"
        "Example: 'Write a song about love and adventure'.\n"
        "Once you send a prompt, our AI will create a unique song just for you! 🎤🎧"
    )
    bot.send_message(message.chat.id, help_text)


@bot.message_handler(func=lambda message: True)
def handle_prompt(message):
    user_prompt = message.text
    song_data = generate_song(user_prompt)
    # with open(generated_song_path, 'rb') as audio_file:
    bot.send_message(
        message.chat.id, "Generating your song please wait...30-40 sec")
    data = get_generated_song(clips=song_data, jwt_token=get_token())
    for i, data in enumerate(song_data):
        bot.send_audio(
            message.chat.id,
            audio=data['audio_url'],
            title="Your Generated Song 🎧",
            performer="Suno AI",
            caption=f"Here's your song based on: *{user_prompt}* 🎵",
            parse_mode="Markdown",
            thumb=data['image_url'],
            thumbnail=data['image_url']
        )
    time.sleep(2)


# @bot.message_handler(['/generate'])
def generate_song(prompt_message):
    # getting jwt token using cookies..
    jwt_token = get_token()
    # generating your song using prompt
    clips_ids = generate_song_request(
        jwt_token=jwt_token, prompt_message=prompt_message)
    # getting the generated song
    jwt_token = get_token()
    for i in range(50):
        time.sleep(1)
        print(i+1, "sec")
    songs_data = get_generated_song(jwt_token=jwt_token, clips=clips_ids)

    return songs_data


def get_token():
    url = "https://clerk.suno.com/v1/client/sessions/sess_2oyZoX2u0l8hMBKzGjtQHfEFXQs/tokens?__clerk_api_version=2021-02-05&_clerk_js_version=5.34.2"
    cookie = "_ga=GA1.1.1468771681.1731605089; ajs_anonymous_id=47551f1e-ab27-4d54-b3fb-860492b3db3d; _cfuvid=vfIbhEBI9WZbnt4vL.iU1bZsc.45PmFB.lSX00IRM5A-1731842665890-0.0.1.1-604800000; __client=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6ImNsaWVudF8yb3FsZmlSaEVYNmVGcUJZS1FnQkFETHdaUU0iLCJyb3RhdGluZ190b2tlbiI6InI0OTZsb3dveWZyemZyemFuYW1yazl2emd1aGgxaHI2NWp2Z3E1bW4ifQ.HApMGZ5OatxjyAaMRU63-Op9mLM3dDnOoM-xCqFFPmivKOdJOhbivSeE28MTUVpdbQc47Lg4b8trWanM-H7Z6QEovmZdovz0tyinj-vIbk0qooFSoyj85r089E84hR1EPUD5eSQbuM9xKK_-k53qmA_4RC1KoeeQ4sVdnnZXT9vSm4JQOfeLY2e9Ddr878_fEdNFpSUR6pGvgSxn6okT_qbOdsIgZHPB0u_hqZ7gE88AM1cLoKuKHnGJB4QCCFeqESHlxsgBkqJIhl3Swsjy7Ifl9PCMVgCHzyc1HBZFE1YeA1bP_ADd7Ytt46fLmZwqKb68HbGLGj6U6rzRjWEhyA; __client_uat=1731843950; __client_uat_U9tcbTPE=1731843950; mp_26ced217328f4737497bd6ba6641ca1c_mixpanel=%7B%22distinct_id%22%3A%20%22e39f281a-001d-4e10-86fd-38a14b4e8ae1%22%2C%22%24device_id%22%3A%20%221932bb4c283d76-0dc49513c2e0e2-26011951-e1000-1932bb4c283d76%22%2C%22%24initial_referrer%22%3A%20%22%24direct%22%2C%22%24initial_referring_domain%22%3A%20%22%24direct%22%2C%22__mps%22%3A%20%7B%7D%2C%22__mpso%22%3A%20%7B%7D%2C%22__mpus%22%3A%20%7B%7D%2C%22__mpa%22%3A%20%7B%7D%2C%22__mpu%22%3A%20%7B%7D%2C%22__mpr%22%3A%20%5B%5D%2C%22__mpap%22%3A%20%5B%5D%2C%22%24user_id%22%3A%20%22e39f281a-001d-4e10-86fd-38a14b4e8ae1%22%7D; _ga_7B0KEDD7XP=GS1.1.1731842666.4.1.1731844392.0.0.0; __cf_bm=jo0wZZugrDcdPzYjTgGYyRkdfWvl5Yb_tBcsPiESj9c-1731845607-1.0.1.1-1tUijiCvw_2r9YS7jXmWbCg45JwUwtSDQ6ompgn1sFfQVwACqc31xZGm0GLITUkLe4aKc.HUCZbsoKtDCiBqHA"
    header = {
        "Cookie": cookie
    }
    rq = requests.post(url=url, headers=header)
    decoded_jwt = rq.content.decode('utf-8')
    jwt_token = json.loads(decoded_jwt)
    jwt_token = jwt_token.get('jwt')
    print(jwt_token)
    return jwt_token


def generate_song_request(jwt_token, prompt_message):
    generate_url = "https://studio-api.prod.suno.com/api/generate/v2/"
    payload = {
        "gpt_description_prompt": prompt_message,
        "mv": "chirp-v3-5",
        "prompt": "",
        "metadata": {
            "lyrics_model": "default"
        },
        "make_instrumental": False,
        "user_uploaded_images_b64": [],
        "generation_type": "TEXT"
    }
    headers = {
        "Content-Type": "application/json",
        "Connection": "keep-alive",
        "Accept-Encoding": "gzip, deflate, br",
        "User-Agent": "PostmanRuntime/7.42.0",
        "Authorization": f"Bearer {jwt_token}",
    }

    try:
        response = requests.post(
            generate_url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Raise exception for HTTP errors

        data = response.json()  # Automatically parse JSON
        clip_ids = [clip.get('id') for clip in data.get('clips', [])]
        print("Clip IDs:", clip_ids)
        return clip_ids

    except requests.exceptions.RequestException as e:
        print("Request Error:", e)
        return []
    except json.JSONDecodeError:
        print("Response JSON Decode Error")
        return []


def get_generated_song(clips, jwt_token):
    if len(clips) < 2:
        print("Error: At least two clip IDs are required.")
        return []

    # API URLs for both clips
    song_url_1 = f"https://studio-api.prod.suno.com/api/feed/v2?ids={clips[0]}&page=5000"
    song_url_2 = f"https://studio-api.prod.suno.com/api/feed/v2?ids={clips[1]}&page=5000"

    header = {
        "Authorization": f"Bearer {jwt_token}"
    }

    try:
        # Fetch and parse the first song
        response_1 = requests.get(url=song_url_1, headers=header)
        response_1.raise_for_status()  # Raise exception for HTTP errors
        parsed_data_1 = response_1.json()
        clip_1 = parsed_data_1.get('clips', [{}])[0]  # Avoid IndexError
        image_url_1 = clip_1.get('image_url')
        audio_url_1 = clip_1.get('audio_url')

        # Fetch and parse the second song
        jwt_token = get_token()
        response_2 = requests.get(url=song_url_2, headers=header)
        response_2.raise_for_status()  # Raise exception for HTTP errors
        parsed_data_2 = response_2.json()
        clip_2 = parsed_data_2.get('clips', [{}])[0]  # Avoid IndexError
        image_url_2 = clip_2.get('image_url')
        audio_url_2 = clip_2.get('audio_url')

        # Combine the results into a single list
        data = [
            {"image_url": image_url_1, "audio_url": audio_url_1},
            {"image_url": image_url_2, "audio_url": audio_url_2}
        ]
        return data

    except requests.exceptions.RequestException as e:
        print(f"Request Error: {str(e)}")
        return []
    except json.JSONDecodeError:
        print("Response JSON Decode Error")
        return []
    except Exception as e:
        print(f"Unexpected Error: {str(e)}")
        return []


# Run the bot
bot.polling(none_stop=True)

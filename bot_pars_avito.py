import json
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import telebot
from API_keys import bot_token

# Replace 'YOUR_TELEGRAM_BOT_TOKEN' with your actual Telegram Bot token
telegram_bot_token = bot_token


class AvitoParse:
    def __init__(self, url: str, count: str, version_main=None):
        self.url = url
        self.count = int(count)  # Convert count to an integer
        self.version_main = version_main
        self.data = []

    def __set_up(self):
        self.driver = uc.Chrome(version_main=self.version_main)

    def __get_url(self):
        self.driver.get(self.url)

    def __paginator(self):
        while self.driver.find_elements(By.CSS_SELECTOR, "[data-marker='pagination-button']") and self.count > 0:
            self.__parse_page()
            self.driver.find_element(By.CSS_SELECTOR, "[data-marker='pagination-button']").click()
            self.count -= 1

    def __parse_page(self):
        titles = self.driver.find_elements(By.CSS_SELECTOR, "[data-marker='item']")
        for title in titles:
            name = title.find_element(By.CSS_SELECTOR, "[itemprop='name']").text
            description = title.find_element(By.CSS_SELECTOR, "[class*='item-description']").text
            url = title.find_element(By.CSS_SELECTOR, "[data-marker='item-title']").get_attribute("href")
            price = title.find_element(By.CSS_SELECTOR, "[itemprop='price']").get_attribute("content")
            data = {
                'name': name,
                'description': description,
                'url': url,
                'price': price
            }
            self.data.append(data)
            print(data)

        self.__save_data()

    def __save_data(self):
        with open('avito_data.json', 'w') as file:
            json.dump(self.data, file)

    def parse(self):
        self.__set_up()
        self.__get_url()
        self.__paginator()


# Create a Telegram bot instance
bot = telebot.TeleBot(telegram_bot_token)


# Define the command handler for '/start' command
@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.reply_to(message, "Welcome to the Avito.ru Parser Bot! Send me the URL and count (optional) to get started.")


# Define the message handler for URL
@bot.message_handler(func=lambda message: True)
def handle_url(message):
    try:
        url = message.text
        if not url.startswith('https://www.avito.ru/'):
            bot.reply_to(message, "Invalid URL. The URL should start with 'https://www.avito.ru/'. Please try again.")
            return

        bot.reply_to(message, "URL received. Now, please send me the count.")
        bot.register_next_step_handler(message, handle_count, url)
    except Exception as e:
        bot.reply_to(message, f"An error occurred: {str(e)}")


# Define the message handler for count
def handle_count(message, url):
    try:
        count = message.text

        avito_parser = AvitoParse(url, count)
        avito_parser.parse()

        # Send the JSON data as a file instead of including it in the message
        with open('avito_data.json', 'rb') as file:
            bot.send_document(message.chat.id, file)

    except Exception as e:
        bot.reply_to(message, f"An error occurred: {str(e)}")


# Run the bot
bot.polling()

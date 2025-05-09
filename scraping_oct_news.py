import requests
from bs4 import BeautifulSoup
import send_mail as send
import datetime
import update_csv_file
from update_csv_file import CsvUpdater
import sys


def create_html_file(post_dic):
    """Here we are generating a .html file, that contains our content. This is for the email."""
    html_head = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            .block {
                border: 1px solid #ccc;
                border-radius: 8px;
                padding: 16px;
                margin-bottom: 16px;
                font-family: Arial, sans-serif;
            }
            .date {
                margin-top: 8px;
                font-size: 10px;
                color: #8B0000;
            }
            .title {
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
            }
            .text {
                margin-top: 8px;
                font-size: 14px;
                color: #333;
            }
            .link {
                margin-top: 12px;
                display: inline-block;
                font-size: 14px;
                color: #2980b9;
                text-decoration: none;
            }
        </style>
    </head>
    <body>
    """

    html_body = ""
    for block in post_dic:
        html_body += f"""
        <div class="block">
            <div class="date">Published on website: {block['date']}</div>
            <br>
            <div class="title">{block['title']}</div>
            <div class="text">{block['text']}</div>
            <br>
            <a class="link" href="{block['link']}">Link to full article</a>
        </div>
        """
    html_footer = """
    </body>
    </html>
    """
    return html_head + html_body + html_footer

def get_website_data(website="https://octnews.org/all-articles/"):
    """Here we scraping the oct-news website. This is legal as I have checked with https://octnews.org/robots.txt
    Here we filter, so that we get the text from the content container and make it useful for us."""
    website = requests.get(website)
    print(f" status = {website.status_code}")
    text_func = BeautifulSoup(website.text, 'html.parser')

    recent_posts_func = text_func.find('div', id='recent-posts-homepage')
    return text_func, recent_posts_func

def generating_output_data(file, title, date, text, link):
    """Here the output data is generated. We get a formated string for .txt files and we get a dictonary to use
    in html files."""
    file = (f"{file}\n"
                     f"(Date: {date})\n"
                     f"Titel:\n {title}\n\n"
                     f"Text:\n {text}\n\n"
                     f" ===>   {link}\n\n"
                     f"----------------------------------------------------------------\n\n")
    dic = {"date": date, "title": title, "text": text, "link": link}
    return file, dic

def save_files(complete,swept_source, html):
    """Here all generated output data are stored in files. We have to .txt outputs and one .html output."""
    with open("./website_data/oct_news_complete.txt", 'w', encoding="utf-8") as file:
        file.write(complete)
        print("Complete ouput saved in file!")
    with open("./website_data/oct_news_swept_source.txt", 'w', encoding="utf-8") as file:
        file.write(swept_source)
        print("Swept source ouput saved in file!")
    with open("./website_data/oct_news_complete.html", 'w', encoding="utf-8") as file:
        file.write(html)
        print("Complete ouput saved in .html file!")

def collecting_data(recent_p, keywords):
    """This function get the complete content of the website that is already filtered.
    It is giving back the content as string and dictonary."""

    complete_post = ""
    complete_post_dic = []
    keyword_theme = ""
    keyword_dic = []

    divs = recent_p.find_all("div", attrs={"style": "clear:both;margin-top:16px"})
    for div in divs:
        link = div.find("a")
        em = div.find("em")
        if link and link.has_attr("href"):
            href = link["href"]
            title = link.get("title", "")
            date = em.get_text(strip=True) if em else ""
            text = div.get_text(separator=" ", strip=True)
            direct_text = ''.join(div.find_all(string=True, recursive=False)).strip()

            if href == "" or title == "":
                continue
            # Here write in file and generate the dictonary to send the mail
            complete_post, dic_temp = generating_output_data(complete_post, title, date, direct_text, href)
            complete_post_dic.append(dic_temp)

            if any(keyword in direct_text.lower() or keyword in text.lower() for keyword in keywords):
                keyword_theme, dic_temp_keyword = generating_output_data(keyword_theme, title, date, direct_text, href)
                keyword_dic.append(dic_temp_keyword)
    return complete_post, complete_post_dic, keyword_theme, keyword_dic

if __name__=="__main__":

    if len(sys.argv) > 1:
        email = sys.argv[1]
    else:
        print("Add the e-mail address to use the option for sending the data.")
        email = None

    new_data = []
    c_post_dic_all = []
    keyword_post_dic_all = []
    csv_writer = CsvUpdater()

    for i in range(0,2):

        if i == 0:
            print(f"Load page 1 ...")
            text, recent_posts = get_website_data()
        if i > 0:
            try:
                print(f"Load page https://octnews.org/all-articles/page/{i+1}/ ...")
                text, recent_posts = get_website_data(f"https://octnews.org/all-articles/page/{i+1}/")
            except Exception as err:
                print(f"Something is went wrong with additional pages of website.\n{err}")

        keywords = ["swept source"]
        c_post, c_post_dic, keyword_post, keyword_post_dic = collecting_data(recent_posts, keywords)
        c_post_dic_all = c_post_dic_all + c_post_dic
        keyword_post_dic_all = keyword_post_dic_all + keyword_post_dic

        #html_content = create_html_file(c_post_dic)
        #save_files(c_post, ss_post, html_content)

    #   Here we send a mail with only the new articles with the keyword in the text
    keyword_data = csv_writer.get_new_data(keyword_post_dic_all)

    if email is not None:
        if keyword_data != []:
            keyword_data = create_html_file(keyword_data)
            print("There are new data for the keywords. Mail will be send!")
            mail = send.ConnectMail(email)
            mail.send_mail(f"New Update for keyword ({datetime.date.today()})", f"{keyword_data}")
            mail.close()

        #   Here we send the email with all new data
        try:
            new_data= csv_writer.add_data(c_post_dic_all)
        except Exception as err:
            print(f"The -csv saver fails. With {err}.")

        if new_data != []:
            new_data_mail = create_html_file(new_data)
            mail = send.ConnectMail(email)
            mail.send_mail(f"New Update of oct-news ({datetime.date.today()})", f"{new_data_mail}")
            mail.close()
        else:
            mail = send.ConnectMail(email)
            mail.send_mail_text(f"No new content ({datetime.date.today()})",
                           "There is new content on the OCT-News website.\n\nHave a great day!")
            mail.close()


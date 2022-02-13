import re
import urllib
import ipaddress
import html.parser
from bs4 import Comment
from pathlib import Path
from urllib.parse import urlparse, parse_qs

class Extractor:
    def __init__(self):
        self.data_dir = "data"

    def n_ext_links(self, links, hostname):
        external_link = 0
        try:
            for link in links:
                if re.search("^https?://" , link):
                    link_hostname = str(urlparse(link).hostname)
                    if not re.search(r'' + str(hostname).replace("www.", "") + '$', link_hostname):
                        external_link = external_link + 1
        except:
            pass

        return external_link

    def callTag(self, tag, body_tag_list):
        for tag in tag.children:
            if (tag.name is not None):
                body_tag_list.append(str(tag.name))
                self.callTag(tag, body_tag_list)

        return body_tag_list

    def general_f(self, soup, hostname):
        general_f_dict = {}
        n_script_tag = 0
        n_style_tag = 0
        n_link_tag = 0
        n_comment_tag = 0
        title_tag = 0
        title_url_brand = 0

        html_length = len(str(soup))

        for script in soup.find_all('script'):
            n_script_tag = n_script_tag + 1

        for style in soup.find_all('style'):
            n_style_tag = n_style_tag + 1

        for link in soup.find_all('link'):
            n_link_tag = n_link_tag + 1

        for comments in soup.findAll(text=lambda text:isinstance(text, Comment)):
            n_comment_tag = n_comment_tag + 1

        if (soup.html is not None):
            html_tag_list = self.callTag(soup.html,list())
        else:
            html_tag_list = list()

        if (soup.body is not None):
            body_tag_list = self.callTag(soup.body,list())
        else:
            body_tag_list = list()

        if (soup.head is not None):
            head_tag_list = self.callTag(soup.head,list())
        else:
            head_tag_list = list()

        if html_tag_list.count("title") == 1:
             if head_tag_list.count("title") == 1:
                    title_tag = 1

        diff_body_children = len(list(dict.fromkeys(body_tag_list)))
        n_body_tag = html_tag_list.count("body")
        n_head_tag = html_tag_list.count("head")

        url_brand = str(hostname).replace("www.", "").split('.')[0]

        title_text = [a.text.strip() for a in soup.find_all('title')] # available titles
        for text in title_text:
            text = text.replace(" ", "")
            if url_brand.lower() in text.lower():
                title_url_brand = 1
            break

        general_f_dict = {'n_script_tag': n_script_tag, 'n_style_tag': n_style_tag,
                      'n_link_tag': n_link_tag, 'n_comment_tag': n_comment_tag, 'title_tag': title_tag,
                      'title_url_brand': title_url_brand, 'html_length': html_length,
                         'diff_body_children': diff_body_children, 'n_body_tag': n_body_tag, 'n_head_tag': n_head_tag}

        return general_f_dict

    def a_tag(self, soup, hostname):
        a_tag_dict = {}

        links = [a['href'].strip() for a in soup.find_all('a', href=True) if a.text] # links with text

        n_hyperlinks = len(links)
        nullpointers_ratio = round((links.count("") + links.count("#"))/n_hyperlinks if n_hyperlinks != 0 else 0, 2)

        external_ratio = round((self.n_ext_links(links, hostname))/n_hyperlinks if n_hyperlinks != 0 else 0, 2)

        a_tag_dict = {'n_hyperlinks': n_hyperlinks, 'nullpointers_ratio': nullpointers_ratio,
                      'external_ratio': external_ratio}

        return a_tag_dict

    def form_tag(self, soup, hostname):
        form_tag_dict = {}
        form_input_b = 0
        form_act = 0
        n_ext_form_act = 0
        n_abn_form_act = 0
        n_int_form_act = 0

        if (soup.find("input") is not None):
            if soup.find("input").find_parent('form'):
                form_input_b = 1

        formTags = soup.findAll('form')
        for form in formTags:
            if form.has_attr('action'):
                form_act_dic = [form.attrs['action']]
                ext_form_act = self.n_ext_links(form_act_dic, hostname)

                if ext_form_act is 1:
                    n_ext_form_act = n_ext_form_act + 1
                else:
                    if (form.attrs['action'].strip() != "#"):
                        if (form.attrs['action'].strip() != "about:blank"):
                            if (form.attrs['action'].strip() != ""):
                                n_int_form_act = n_int_form_act + 1
                            else:
                                n_abn_form_act = n_abn_form_act + 1
                        else:
                            n_abn_form_act = n_abn_form_act + 1
                    else:
                        n_abn_form_act = n_abn_form_act + 1
            form_act = form_act + 1

        ext_form_act_ratio = round(n_ext_form_act/form_act if form_act != 0 else 0, 2)
        abn_form_act_ratio = round(n_abn_form_act/form_act if form_act != 0 else 0, 2)
        int_form_act_ratio = round(n_int_form_act/form_act if form_act != 0 else 0, 2)

        form_tag_dict = {'ext_form_act_ratio': ext_form_act_ratio, 'abn_form_act_ratio': abn_form_act_ratio,
                      'int_form_act_ratio': int_form_act_ratio, 'form_input_b': form_input_b}

        return form_tag_dict

    def ext_resource(self, soup, hostname):
        images = [a['src'].strip() for a in soup.find_all('img', src=True)] # images links
        scripts = [a['src'].strip() for a in soup.find_all('script', src=True)] # script links
        links = [a['href'].strip() for a in soup.find_all('link', href=True)] # style links

        ext_images = self.n_ext_links(images, hostname)
        ext_scripts = self.n_ext_links(scripts, hostname)
        ext_links = self.n_ext_links(links, hostname)

        total_res_links = len(images) + len(scripts) + len(links)
        total_ext_res = ext_images + ext_scripts + ext_links

        ext_resource_ratio = round(total_ext_res/total_res_links if total_res_links != 0 else 0, 2)

        return ext_resource_ratio

    def favicon_feature(self, soup, url_t, hostname): #https://mail.ma5doom.com/favicon.ico, http://ymcmblog.hu/favicon.ico,
        #https://www.ebay.com/favicon.ico
        favicon = 0
        shortcut_icon_link = soup.find("link", rel="shortcut icon")
        if shortcut_icon_link is None:
            icon_link = soup.find("link", rel="icon")
            if icon_link is not None:
                if icon_link.has_attr('href'):
                    icon_link_dic = [icon_link["href"]]
                    ext_favicon = self.n_ext_links(icon_link_dic, hostname)
                    if ext_favicon is 0:
                        if icon_link["href"].strip() != "":
                            if icon_link["href"].strip() != "#":
                                favicon = 1
        else:
            if shortcut_icon_link.has_attr('href'):
                icon_link_dic = [shortcut_icon_link["href"]]
                ext_favicon = self.n_ext_links(icon_link_dic, hostname)
                if ext_favicon is 0:
                    if shortcut_icon_link["href"].strip() != "":
                        if shortcut_icon_link["href"].strip() != "#":
                            favicon = 1

        if shortcut_icon_link is None and icon_link is None:
            url_t = urlparse(url_t).scheme + "://" + urlparse(url_t).hostname + "/favicon.ico"
            headers = { 'User-Agent' : 'Firefox', 'Accept-Language' : 'en-US' }
            req = urllib.request.Request(url_t, None, headers)

            try:
                response = urllib.request.urlopen(req, timeout=20)
                r_length = len(response.read())
                if r_length > 0:
                    favicon = 1
            except:
                pass

        return favicon

    def disabled_status(self, soup, hostname):
        disabled_div_1 = [a['style'] for a in soup.find_all('div', style="visibility: hidden")]
        disabled_div_2 = [a['style'] for a in soup.find_all('div', style="display: none")]
        disabled_button = [a['disabled'] for a in soup.find_all('button', disabled="disabled")]
        disabled_input_1 = [a['disabled'] for a in soup.find_all('input', disabled="disabled")]
        disabled_input_2 = [a['type'] for a in soup.find_all('input', type="hidden")]

        n_disabled_tags = len(disabled_div_1) + len(disabled_div_2) + len(disabled_button) + len(disabled_input_1) + len(disabled_input_2)

        return n_disabled_tags

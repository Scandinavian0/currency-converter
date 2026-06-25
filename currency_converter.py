# -*- coding: utf-8 -*-
import html
import json
import threading
import urllib.error
import urllib.request
from datetime import date, datetime
from html.parser import HTMLParser
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk


APP_NAME = "实时货币等值转换"
BOC_RATE_URL = "https://www.bankofchina.com/sourcedb/whpj/enindex_1619.html"
REFERENCE_RATE_URL = "https://open.er-api.com/v6/latest/CNY"
CACHE_FILE = Path.home() / ".currency_converter_rates.json"
STATE_FILE = Path.home() / ".currency_converter_state.json"

RATE_MODES = {
    "buying": "出口收汇（现汇买入价）",
    "selling": "进口付款（现汇卖出价）",
    "middle": "中间价（参考/记账）",
    "cash_buying": "现钞买入价",
    "cash_selling": "现钞卖出价",
}
DEFAULT_MODE = "buying"


CURRENCY_NAMES = {
    "AED": "阿联酋迪拉姆",
    "AUD": "澳大利亚元",
    "BRL": "巴西雷亚尔",
    "CAD": "加拿大元",
    "CHF": "瑞士法郎",
    "CNY": "人民币",
    "DKK": "丹麦克朗",
    "EUR": "欧元",
    "GBP": "英镑",
    "HKD": "港币",
    "IDR": "印尼盾",
    "INR": "印度卢比",
    "JPY": "日元",
    "KRW": "韩元",
    "MOP": "澳门元",
    "MYR": "马来西亚林吉特",
    "NOK": "挪威克朗",
    "NZD": "新西兰元",
    "PHP": "菲律宾比索",
    "RUB": "俄罗斯卢布",
    "SAR": "沙特里亚尔",
    "SEK": "瑞典克朗",
    "SGD": "新加坡元",
    "THB": "泰铢",
    "TRY": "土耳其里拉",
    "TWD": "新台币",
    "USD": "美元",
    "VND": "越南盾",
    "ZAR": "南非兰特",
}

CURRENCY_NAMES.update({
    "AFN": "阿富汗尼",
    "ALL": "阿尔巴尼亚列克",
    "AMD": "亚美尼亚德拉姆",
    "ANG": "荷属安的列斯盾",
    "AOA": "安哥拉宽扎",
    "ARS": "阿根廷比索",
    "AWG": "阿鲁巴弗罗林",
    "AZN": "阿塞拜疆马纳特",
    "BAM": "波黑可兑换马克",
    "BBD": "巴巴多斯元",
    "BDT": "孟加拉塔卡",
    "BGN": "保加利亚列弗",
    "BHD": "巴林第纳尔",
    "BIF": "布隆迪法郎",
    "BMD": "百慕大元",
    "BND": "文莱元",
    "BOB": "玻利维亚诺",
    "BSD": "巴哈马元",
    "BTN": "不丹努尔特鲁姆",
    "BWP": "博茨瓦纳普拉",
    "BYN": "白俄罗斯卢布",
    "BZD": "伯利兹元",
    "CDF": "刚果法郎",
    "CLP": "智利比索",
    "COP": "哥伦比亚比索",
    "CRC": "哥斯达黎加科朗",
    "CUP": "古巴比索",
    "CVE": "佛得角埃斯库多",
    "CZK": "捷克克朗",
    "DJF": "吉布提法郎",
    "DOP": "多米尼加比索",
    "DZD": "阿尔及利亚第纳尔",
    "EGP": "埃及镑",
    "ERN": "厄立特里亚纳克法",
    "ETB": "埃塞俄比亚比尔",
    "FJD": "斐济元",
    "FKP": "福克兰群岛镑",
    "FOK": "法罗群岛克朗",
    "GEL": "格鲁吉亚拉里",
    "GGP": "根西镑",
    "GHS": "加纳塞地",
    "GIP": "直布罗陀镑",
    "GMD": "冈比亚达拉西",
    "GNF": "几内亚法郎",
    "GTQ": "危地马拉格查尔",
    "GYD": "圭亚那元",
    "HNL": "洪都拉斯伦皮拉",
    "HRK": "克罗地亚库纳",
    "HTG": "海地古德",
    "HUF": "匈牙利福林",
    "ILS": "以色列新谢克尔",
    "IMP": "马恩岛镑",
    "IQD": "伊拉克第纳尔",
    "IRR": "伊朗里亚尔",
    "ISK": "冰岛克朗",
    "JEP": "泽西镑",
    "JMD": "牙买加元",
    "JOD": "约旦第纳尔",
    "KES": "肯尼亚先令",
    "KGS": "吉尔吉斯斯坦索姆",
    "KHR": "柬埔寨瑞尔",
    "KID": "基里巴斯元",
    "KMF": "科摩罗法郎",
    "KWD": "科威特第纳尔",
    "KYD": "开曼群岛元",
    "KZT": "哈萨克斯坦坚戈",
    "LAK": "老挝基普",
    "LBP": "黎巴嫩镑",
    "LKR": "斯里兰卡卢比",
    "LRD": "利比里亚元",
    "LSL": "莱索托洛蒂",
    "LYD": "利比亚第纳尔",
    "MAD": "摩洛哥迪拉姆",
    "MDL": "摩尔多瓦列伊",
    "MGA": "马达加斯加阿里亚里",
    "MKD": "北马其顿代纳尔",
    "MMK": "缅甸元",
    "MNT": "蒙古图格里克",
    "MRU": "毛里塔尼亚乌吉亚",
    "MUR": "毛里求斯卢比",
    "MVR": "马尔代夫拉菲亚",
    "MWK": "马拉维克瓦查",
    "MXN": "墨西哥比索",
    "MZN": "莫桑比克梅蒂卡尔",
    "NAD": "纳米比亚元",
    "NGN": "尼日利亚奈拉",
    "NIO": "尼加拉瓜科多巴",
    "NPR": "尼泊尔卢比",
    "OMR": "阿曼里亚尔",
    "PAB": "巴拿马巴波亚",
    "PEN": "秘鲁索尔",
    "PGK": "巴布亚新几内亚基那",
    "PKR": "巴基斯坦卢比",
    "PLN": "波兰兹罗提",
    "PYG": "巴拉圭瓜拉尼",
    "QAR": "卡塔尔里亚尔",
    "RON": "罗马尼亚列伊",
    "RSD": "塞尔维亚第纳尔",
    "RWF": "卢旺达法郎",
    "SBD": "所罗门群岛元",
    "SCR": "塞舌尔卢比",
    "SDG": "苏丹镑",
    "SHP": "圣赫勒拿镑",
    "SLE": "塞拉利昂利昂",
    "SOS": "索马里先令",
    "SRD": "苏里南元",
    "SSP": "南苏丹镑",
    "STN": "圣多美和普林西比多布拉",
    "SYP": "叙利亚镑",
    "SZL": "斯威士兰里兰吉尼",
    "TJS": "塔吉克斯坦索莫尼",
    "TMT": "土库曼斯坦马纳特",
    "TND": "突尼斯第纳尔",
    "TOP": "汤加潘加",
    "TTD": "特立尼达和多巴哥元",
    "TVD": "图瓦卢元",
    "TZS": "坦桑尼亚先令",
    "UAH": "乌克兰格里夫纳",
    "UGX": "乌干达先令",
    "UYU": "乌拉圭比索",
    "UZS": "乌兹别克斯坦索姆",
    "VES": "委内瑞拉玻利瓦尔",
    "VUV": "瓦努阿图瓦图",
    "WST": "萨摩亚塔拉",
    "XAF": "中非法郎",
    "XCD": "东加勒比元",
    "XDR": "特别提款权",
    "XOF": "西非法郎",
    "XPF": "太平洋法郎",
    "YER": "也门里亚尔",
    "ZMW": "赞比亚克瓦查",
    "ZWL": "津巴布韦元",
})


FALLBACK_RATE_SETS = {
    "buying": {
        "CNY": 1.0,
        "USD": 6.7946,
        "EUR": 7.7030,
        "GBP": 8.9335,
        "JPY": 0.04204,
        "HKD": 0.8664,
        "AUD": 4.6755,
        "CAD": 4.7633,
        "SGD": 5.2271,
        "KRW": 0.00438,
    },
    "selling": {
        "CNY": 1.0,
        "USD": 6.8232,
        "EUR": 7.7595,
        "GBP": 8.9999,
        "JPY": 0.04237,
        "HKD": 0.8698,
        "AUD": 4.7127,
        "CAD": 4.8007,
        "SGD": 5.2665,
        "KRW": 0.00447,
    },
    "middle": {
        "CNY": 1.0,
        "USD": 6.8209,
        "EUR": 7.7349,
        "GBP": 8.9682,
        "JPY": 0.04214,
        "HKD": 0.8701,
        "AUD": 4.6992,
        "CAD": 4.7853,
        "SGD": 5.2507,
        "KRW": 0.00442,
    },
    "cash_buying": {},
    "cash_selling": {},
}
FALLBACK_RATE_SETS["cash_buying"] = dict(FALLBACK_RATE_SETS["buying"])
FALLBACK_RATE_SETS["cash_selling"] = dict(FALLBACK_RATE_SETS["selling"])


class BocRateTableParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.in_price_table = False
        self.in_row = False
        self.in_cell = False
        self.current_name = ""
        self.current_cells = []
        self.current_text = []
        self.rows = []

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag == "table" and attrs_dict.get("id") == "priceTable":
            self.in_price_table = True
        if not self.in_price_table:
            return
        if tag == "tr":
            self.in_row = True
            self.current_name = attrs_dict.get("data-currency", "")
            self.current_cells = []
        elif self.in_row and tag in {"td", "th"}:
            self.in_cell = True
            self.current_text = []

    def handle_endtag(self, tag):
        if self.in_price_table and self.in_cell and tag in {"td", "th"}:
            text = html.unescape("".join(self.current_text)).replace("\xa0", " ").strip()
            self.current_cells.append(text)
            self.current_text = []
            self.in_cell = False
        elif self.in_price_table and self.in_row and tag == "tr":
            if self.current_name and len(self.current_cells) >= 7:
                self.rows.append((self.current_name.strip(), self.current_cells[:7]))
            self.in_row = False
        elif self.in_price_table and tag == "table":
            self.in_price_table = False

    def handle_data(self, data):
        if self.in_cell:
            self.current_text.append(data)


class RateStore:
    def __init__(self):
        self.rate_sets = {mode: dict(rates) for mode, rates in FALLBACK_RATE_SETS.items()}
        self.currency_names = dict(CURRENCY_NAMES)
        self.last_update = None
        self.source = "内置备用中行牌价"
        self.pub_time = None
        self.reference_codes = set()
        self.load_cache()

    def load_cache(self):
        if not CACHE_FILE.exists():
            return
        try:
            data = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return

        if data.get("provider") != "bank-of-china":
            return

        rate_sets = data.get("rate_sets", {})
        if not isinstance(rate_sets, dict):
            return

        cleaned = {}
        for mode in RATE_MODES:
            mode_rates = rate_sets.get(mode, {})
            if not isinstance(mode_rates, dict):
                continue
            valid_rates = {}
            for code, rate in mode_rates.items():
                try:
                    numeric = float(rate)
                except (TypeError, ValueError):
                    continue
                if numeric > 0:
                    valid_rates[code.upper()] = numeric
            if valid_rates:
                valid_rates["CNY"] = 1.0
                cleaned[mode] = valid_rates

        if cleaned:
            for mode, rates in cleaned.items():
                self.rate_sets[mode] = rates
            names = data.get("currency_names", {})
            if isinstance(names, dict):
                self.currency_names.update({code.upper(): str(name) for code, name in names.items() if name})
            self.last_update = data.get("last_update")
            self.source = data.get("source", "中国银行外汇牌价缓存")
            self.pub_time = data.get("pub_time")
            self.reference_codes = set(data.get("reference_codes", []))

    def save_cache(self):
        payload = {
            "provider": "bank-of-china",
            "last_update": self.last_update,
            "source": self.source,
            "pub_time": self.pub_time,
            "currency_names": self.currency_names,
            "rate_sets": self.rate_sets,
            "reference_codes": sorted(self.reference_codes),
        }
        CACHE_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def needs_update(self):
        return self.last_update != date.today().isoformat() or "中国银行" not in self.source

    def update_from_network(self):
        request = urllib.request.Request(
            BOC_RATE_URL,
            headers={
                "User-Agent": "Mozilla/5.0 CurrencyConverter/1.0",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            },
        )
        with urllib.request.urlopen(request, timeout=15) as response:
            body = response.read()

        text = body.decode("utf-8", errors="replace")
        parser = BocRateTableParser()
        parser.feed(text)

        if not parser.rows:
            raise RuntimeError("没有从中国银行页面解析到汇率表")

        rate_sets = {mode: {"CNY": 1.0} for mode in RATE_MODES}
        currency_names = dict(self.currency_names)
        pub_times = []

        for chinese_name, cells in parser.rows:
            code = cells[0].strip().upper()
            if not code or code == "CNY":
                continue
            currency_names[code] = chinese_name
            pub_times.append(cells[6].strip())

            values = {
                "buying": cells[1],
                "cash_buying": cells[2],
                "selling": cells[3],
                "cash_selling": cells[4],
                "middle": cells[5],
            }
            for mode, raw_value in values.items():
                rate = self.parse_boc_rate(raw_value)
                if rate:
                    rate_sets[mode][code] = rate

        if "USD" not in rate_sets["buying"] or rate_sets["buying"]["USD"] <= 0:
            raise RuntimeError("中国银行页面缺少美元现汇买入价")

        self.reference_codes = set()
        self.merge_reference_rates(rate_sets, currency_names)

        for mode in RATE_MODES:
            if len(rate_sets[mode]) <= 1:
                rate_sets[mode] = dict(self.rate_sets.get(mode, {"CNY": 1.0}))

        self.rate_sets = rate_sets
        self.currency_names = currency_names
        self.last_update = date.today().isoformat()
        self.source = "中国银行外汇牌价"
        self.pub_time = max(pub_times) if pub_times else datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        self.save_cache()

    def merge_reference_rates(self, rate_sets, currency_names):
        try:
            request = urllib.request.Request(REFERENCE_RATE_URL, headers={"User-Agent": "currency-converter/1.0"})
            with urllib.request.urlopen(request, timeout=12) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError):
            return

        if payload.get("result") != "success":
            return

        for code, value in payload.get("rates", {}).items():
            code = code.upper()
            if code == "CNY":
                continue
            try:
                numeric = float(value)
            except (TypeError, ValueError):
                continue
            if numeric <= 0:
                continue

            cny_rate = 1 / numeric
            if code not in rate_sets["middle"]:
                self.reference_codes.add(code)
            currency_names.setdefault(code, CURRENCY_NAMES.get(code, code))
            for mode in RATE_MODES:
                rate_sets[mode].setdefault(code, cny_rate)

    @staticmethod
    def parse_boc_rate(raw_value):
        text = raw_value.strip().replace(",", "")
        if not text:
            return None
        try:
            value = float(text)
        except ValueError:
            return None
        if value <= 0:
            return None
        return value / 100

    def rates_for_mode(self, mode):
        return self.rate_sets.get(mode) or self.rate_sets[DEFAULT_MODE]


class ScrollableFrame(tk.Frame):
    def __init__(self, master, bg):
        super().__init__(master, bg=bg)
        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.content = tk.Frame(self.canvas, bg=bg)

        self.window_id = self.canvas.create_window((0, 0), window=self.content, anchor="nw")
        self.canvas.configure(yscrollcommand=self._on_scrollbar)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self.scrollbar.pack_forget()

        self.content.bind("<Configure>", self._sync_scroll_region)
        self.canvas.bind("<Configure>", self._sync_content_width)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", lambda event: self.canvas.yview_scroll(-1, "units"))
        self.canvas.bind_all("<Button-5>", lambda event: self.canvas.yview_scroll(1, "units"))

    def _sync_scroll_region(self, _event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.after_idle(self._toggle_scrollbar)

    def _sync_content_width(self, event):
        self.canvas.itemconfigure(self.window_id, width=event.width)
        self.after_idle(self._toggle_scrollbar)

    def _toggle_scrollbar(self):
        bbox = self.canvas.bbox("all")
        if not bbox:
            self.scrollbar.pack_forget()
            return
        content_height = bbox[3] - bbox[1]
        if content_height > self.canvas.winfo_height():
            if not self.scrollbar.winfo_ismapped():
                self.scrollbar.pack(side="right", fill="y")
        elif self.scrollbar.winfo_ismapped():
            self.scrollbar.pack_forget()

    def _on_scrollbar(self, first, last):
        self.scrollbar.set(first, last)
        self._toggle_scrollbar()

    def _on_mousewheel(self, event):
        if self.winfo_containing(event.x_root, event.y_root):
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")


class SearchableCurrencyCombobox(ttk.Combobox):
    def __init__(self, master, values, **kwargs):
        super().__init__(master, values=values, state="normal", **kwargs)
        self.all_values = list(values)
        self.bind("<KeyRelease>", self._filter_values)
        self.bind("<FocusIn>", self._show_all_if_empty)

    def set_all_values(self, values):
        current = self.get()
        self.all_values = list(values)
        self.configure(values=self.all_values)
        if current:
            self.set(current)

    def _show_all_if_empty(self, _event=None):
        if not self.get().strip():
            self.configure(values=self.all_values)

    def _filter_values(self, event):
        if event.keysym in {"Up", "Down", "Left", "Right", "Return", "Escape", "Tab"}:
            return

        keyword = self.get().strip().lower()
        if not keyword:
            matches = self.all_values
        else:
            matches = [label for label in self.all_values if self.matches(label, keyword)]
        self.configure(values=matches)

        if matches:
            self.after_idle(self._open_dropdown)

    def _open_dropdown(self):
        if self.winfo_exists() and self.focus_get() is self:
            try:
                self.tk.call("ttk::combobox::Post", self)
            except tk.TclError:
                pass

    @staticmethod
    def matches(label, keyword):
        label_lower = label.lower()
        code = ""
        name = label
        if "(" in label and label.endswith(")"):
            name = label.rsplit("(", 1)[0].strip()
            code = label.rsplit("(", 1)[1][:-1].strip().lower()
        return keyword in label_lower or keyword in name.lower() or keyword in code


class CurrencyConverterApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title(APP_NAME)
        self.geometry("720x780")
        self.minsize(500, 540)
        self.configure(bg="#1f232b")

        self.store = RateStore()
        self.app_state = self.load_app_state()
        self.rate_mode = self.app_state.get("rate_mode", DEFAULT_MODE)
        if self.rate_mode not in RATE_MODES:
            self.rate_mode = DEFAULT_MODE
        self.amount_rows = []
        self.active_row = None
        self.is_updating = False
        self.available_codes = self.sorted_codes()

        self._build_styles()
        self._build_ui()
        self.restore_amount_rows()
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.recalculate_from_active()
        self.update_status()
        self.refresh_rates_if_needed()

    def load_app_state(self):
        if not STATE_FILE.exists():
            return {}
        try:
            data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {}
        if not isinstance(data, dict):
            return {}
        return data

    def save_app_state(self):
        codes = []
        for row in self.amount_rows:
            code = self.code_from_label(row["currency_var"].get())
            if code in self.rates():
                codes.append(code)
        payload = {
            "rate_mode": self.rate_mode,
            "display_codes": codes or ["CNY", "USD"],
        }
        try:
            STATE_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        except OSError:
            pass

    def restore_amount_rows(self):
        saved_codes = self.app_state.get("display_codes")
        if isinstance(saved_codes, list) and saved_codes:
            codes = [str(code).upper() for code in saved_codes if str(code).upper() in self.rates()]
            if codes:
                for code in codes:
                    self.add_amount_row(code, "0")
                self.active_row = self.amount_rows[0]
                return

        usd_rate = self.rates().get("USD", 6.8)
        self.add_amount_row("CNY", self.format_amount(usd_rate))
        self.add_amount_row("USD", "1")
        self.active_row = self.amount_rows[1]

    def reset_state(self):
        try:
            if STATE_FILE.exists():
                STATE_FILE.unlink()
        except OSError:
            pass

        for row in list(self.amount_rows):
            row["frame"].destroy()
        self.amount_rows.clear()
        self.rate_mode = DEFAULT_MODE
        self.mode_var.set(RATE_MODES[self.rate_mode])
        self.refresh_currency_options()
        usd_rate = self.rates().get("USD", 6.8)
        self.add_amount_row("CNY", self.format_amount(usd_rate))
        self.add_amount_row("USD", "1")
        self.active_row = self.amount_rows[1]
        self.recalculate_from_active()
        self.update_status("已重置。下次打开会恢复默认人民币/美元初始化。")

    def on_close(self):
        self.save_app_state()
        self.destroy()

    def _build_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure(
            "Dark.TCombobox",
            fieldbackground="#252932",
            background="#252932",
            foreground="#ecf1f8",
            arrowcolor="#aab2c0",
            bordercolor="#8b94a3",
            lightcolor="#8b94a3",
            darkcolor="#8b94a3",
            padding=6,
        )
        style.map(
            "Dark.TCombobox",
            fieldbackground=[("readonly", "#252932")],
            foreground=[("readonly", "#ecf1f8")],
            selectbackground=[("readonly", "#2f6fac")],
            selectforeground=[("readonly", "#ffffff")],
        )

    def _build_ui(self):
        outer = tk.Frame(self, bg="#1f232b")
        outer.pack(fill="both", expand=True)

        scroller = ScrollableFrame(outer, bg="#1f232b")
        scroller.pack(fill="both", expand=True)
        root = tk.Frame(scroller.content, bg="#1f232b", padx=18, pady=18)
        root.pack(fill="both", expand=True)

        tk.Label(
            root,
            text=APP_NAME,
            bg="#1f232b",
            fg="#f5f7fb",
            font=("Microsoft YaHei UI", 18, "bold"),
            anchor="w",
        ).pack(fill="x")

        self.status_var = tk.StringVar()
        tk.Label(
            root,
            textvariable=self.status_var,
            bg="#1f232b",
            fg="#aab2c0",
            font=("Microsoft YaHei UI", 10),
            anchor="w",
            wraplength=650,
            justify="left",
        ).pack(fill="x", pady=(4, 16))

        mode_box = tk.Frame(root, bg="#252932", padx=10, pady=10)
        mode_box.pack(fill="x", pady=(0, 14))
        mode_box.columnconfigure(1, weight=1)

        tk.Label(
            mode_box,
            text="汇率口径",
            bg="#252932",
            fg="#dce3ee",
            font=("Microsoft YaHei UI", 10, "bold"),
            anchor="w",
        ).grid(row=0, column=0, sticky="w", padx=(0, 10))

        self.mode_var = tk.StringVar(value=RATE_MODES[self.rate_mode])
        self.mode_picker = ttk.Combobox(
            mode_box,
            textvariable=self.mode_var,
            values=list(RATE_MODES.values()),
            state="readonly",
            style="Dark.TCombobox",
            font=("Microsoft YaHei UI", 11),
            height=len(RATE_MODES),
        )
        self.mode_picker.grid(row=0, column=1, sticky="ew", ipady=5)
        self.mode_picker.bind("<<ComboboxSelected>>", self.on_mode_changed)

        self.amount_frame = tk.Frame(root, bg="#1f232b")
        self.amount_frame.pack(fill="x")

        action_bar = tk.Frame(root, bg="#1f232b")
        action_bar.pack(fill="x", pady=(8, 20))

        tk.Button(
            action_bar,
            text="+ 添加金额输入框",
            command=lambda: self.add_amount_row(),
            bg="#2e7d5b",
            fg="#ffffff",
            activebackground="#38966e",
            activeforeground="#ffffff",
            relief="flat",
            padx=12,
            pady=8,
            cursor="hand2",
        ).pack(side="left")

        tk.Button(
            action_bar,
            text="立即联网更新中行牌价",
            command=lambda: self.refresh_rates_if_needed(force=True),
            bg="#3a6ea5",
            fg="#ffffff",
            activebackground="#477fb9",
            activeforeground="#ffffff",
            relief="flat",
            padx=12,
            pady=8,
            cursor="hand2",
        ).pack(side="left", padx=(10, 0))

        tk.Button(
            action_bar,
            text="重置",
            command=self.reset_state,
            bg="#5a6170",
            fg="#ffffff",
            activebackground="#6a7282",
            activeforeground="#ffffff",
            relief="flat",
            padx=12,
            pady=8,
            cursor="hand2",
        ).pack(side="left", padx=(10, 0))

        tk.Label(
            root,
            text="添加常用币种",
            bg="#1f232b",
            fg="#f5f7fb",
            font=("Microsoft YaHei UI", 13, "bold"),
            anchor="w",
        ).pack(fill="x", pady=(2, 8))

        picker = tk.Frame(root, bg="#252932", padx=10, pady=10)
        picker.pack(fill="x")
        picker.columnconfigure(0, weight=1)

        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(
            picker,
            textvariable=self.search_var,
            bg="#1f232b",
            fg="#f5f7fb",
            insertbackground="#f5f7fb",
            relief="solid",
            bd=1,
            font=("Microsoft YaHei UI", 11),
        )
        self.search_entry.grid(row=0, column=0, sticky="ew", ipady=7, padx=(0, 8))
        self.search_entry.insert(0, "输入中文名称或代码，如：美元、USD、日本、JPY")
        self.search_entry.bind("<FocusIn>", self.clear_search_placeholder)
        self.search_entry.bind("<KeyRelease>", self.update_search_results)
        self.search_entry.bind("<Return>", lambda _event: self.add_selected_currency())

        tk.Button(
            picker,
            text="添加所选币种",
            command=self.add_selected_currency,
            bg="#3a6ea5",
            fg="#ffffff",
            activebackground="#477fb9",
            activeforeground="#ffffff",
            relief="flat",
            padx=12,
            pady=7,
            cursor="hand2",
        ).grid(row=0, column=1)

        result_box = tk.Frame(picker, bg="#252932")
        result_box.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(8, 0))
        result_box.columnconfigure(0, weight=1)

        self.search_results = tk.Listbox(
            result_box,
            height=8,
            bg="#1f232b",
            fg="#f5f7fb",
            selectbackground="#2f6fac",
            selectforeground="#ffffff",
            activestyle="none",
            relief="solid",
            bd=1,
            font=("Microsoft YaHei UI", 10),
            exportselection=False,
        )
        self.search_results.grid(row=0, column=0, sticky="ew")
        result_scroll = ttk.Scrollbar(result_box, orient="vertical", command=self.search_results.yview)
        result_scroll.grid(row=0, column=1, sticky="ns")
        self.search_results.configure(yscrollcommand=result_scroll.set)
        self.search_results.bind("<Double-Button-1>", lambda _event: self.add_selected_currency())
        self.search_results.bind("<Return>", lambda _event: self.add_selected_currency())
        self.update_search_results()

        self.rate_info_var = tk.StringVar()
        tk.Label(
            root,
            textvariable=self.rate_info_var,
            bg="#1f232b",
            fg="#aab2c0",
            font=("Microsoft YaHei UI", 10),
            anchor="w",
            justify="left",
            wraplength=650,
        ).pack(fill="x", pady=(12, 0))

    def rates(self):
        return self.store.rates_for_mode(self.rate_mode)

    def sorted_codes(self):
        codes = sorted(self.rates())
        preferred = [code for code in ("CNY", "USD", "EUR", "JPY", "GBP", "HKD", "AUD", "CAD", "SGD", "KRW") if code in codes]
        return preferred + [code for code in codes if code not in preferred]

    def currency_labels(self):
        return [self.label_for(code) for code in self.available_codes]

    def clear_search_placeholder(self, _event=None):
        if self.search_var.get() == "输入中文名称或代码，如：美元、USD、日本、JPY":
            self.search_var.set("")
            self.update_search_results()

    def update_search_results(self, _event=None):
        if not hasattr(self, "search_results"):
            return
        keyword = self.search_var.get().strip().lower()
        if keyword == "输入中文名称或代码，如：美元、usd、日本、jpy":
            keyword = ""

        matches = []
        for code in self.available_codes:
            label = self.label_for(code)
            name = self.store.currency_names.get(code, code)
            if not keyword or keyword in code.lower() or keyword in name.lower() or keyword in label.lower():
                matches.append(label)

        self.search_results.delete(0, tk.END)
        for label in matches[:80]:
            self.search_results.insert(tk.END, label)
        if matches:
            self.search_results.selection_set(0)

    def label_for(self, code):
        name = self.store.currency_names.get(code, code)
        if code in self.store.reference_codes:
            return f"{name} ({code}) - 参考"
        return f"{name} ({code})"

    def code_from_label(self, label):
        text = label.strip()
        if "(" in text and ")" in text:
            code = text.rsplit("(", 1)[1].split(")", 1)[0].strip().upper()
            if code in self.rates():
                return code
        upper_text = text.upper()
        if upper_text in self.rates():
            return upper_text
        for code in self.available_codes:
            if text == self.store.currency_names.get(code, code):
                return code
        lowered = text.lower()
        for code in self.available_codes:
            name = self.store.currency_names.get(code, code)
            if lowered and (lowered in code.lower() or lowered in name.lower() or lowered in self.label_for(code).lower()):
                return code
        return "CNY"

    def add_amount_row(self, code="USD", amount=""):
        if code not in self.rates():
            code = "USD" if "USD" in self.rates() else "CNY"

        row = tk.Frame(self.amount_frame, bg="#1f232b")
        row.pack(fill="x", pady=5)
        row.columnconfigure(0, weight=1)

        amount_var = tk.StringVar(value=amount)
        currency_var = tk.StringVar(value=self.label_for(code))

        entry = tk.Entry(
            row,
            textvariable=amount_var,
            bg="#252932",
            fg="#f5f7fb",
            insertbackground="#f5f7fb",
            relief="solid",
            bd=1,
            font=("Segoe UI", 14),
        )
        entry.grid(row=0, column=0, sticky="ew", ipady=10)

        combo = ttk.Combobox(
            row,
            textvariable=currency_var,
            values=self.currency_labels(),
            state="readonly",
            width=20,
            style="Dark.TCombobox",
            font=("Microsoft YaHei UI", 11),
            height=18,
        )
        combo.grid(row=0, column=1, sticky="ew", padx=(8, 8), ipady=5)

        delete_btn = tk.Button(
            row,
            text="×",
            command=lambda: self.delete_amount_row(row_info),
            bg="#4b2530",
            fg="#ffffff",
            activebackground="#6b3140",
            activeforeground="#ffffff",
            relief="flat",
            width=3,
            pady=7,
            font=("Segoe UI", 13, "bold"),
            cursor="hand2",
        )
        delete_btn.grid(row=0, column=2, sticky="e")

        row_info = {
            "frame": row,
            "entry": entry,
            "combo": combo,
            "amount_var": amount_var,
            "currency_var": currency_var,
        }
        self.amount_rows.append(row_info)

        entry.bind("<KeyRelease>", lambda _event, info=row_info: self.on_amount_changed(info))
        entry.bind("<FocusIn>", lambda _event, info=row_info: self.set_active_row(info))
        combo.bind("<<ComboboxSelected>>", lambda _event, info=row_info: self.on_currency_changed(info))
        return row_info

    def add_selected_currency(self):
        selected = self.search_results.curselection() if hasattr(self, "search_results") else ()
        if selected:
            label = self.search_results.get(selected[0])
        else:
            label = self.search_var.get()
        code = self.code_from_label(label)
        self.add_amount_row(code)
        self.recalculate_from_active()
        self.save_app_state()

    def delete_amount_row(self, row_info):
        if len(self.amount_rows) <= 1:
            messagebox.showinfo("无法删除", "至少保留一个金额输入框。")
            return
        self.amount_rows.remove(row_info)
        row_info["frame"].destroy()
        if self.active_row is row_info:
            self.active_row = self.amount_rows[0]
        self.recalculate_from_active()
        self.save_app_state()

    def on_mode_changed(self, _event=None):
        selected = self.mode_var.get()
        for mode, label in RATE_MODES.items():
            if label == selected:
                self.rate_mode = mode
                break
        self.refresh_currency_options()
        self.recalculate_from_active()
        self.update_status()
        self.save_app_state()

    def refresh_currency_options(self):
        self.available_codes = self.sorted_codes()
        labels = self.currency_labels()
        self.update_search_results()

        for row in self.amount_rows:
            current_code = self.code_from_label(row["currency_var"].get())
            row["combo"].configure(values=labels)
            if current_code in self.rates():
                row["currency_var"].set(self.label_for(current_code))
            else:
                row["currency_var"].set(self.label_for("CNY"))

    def set_active_row(self, row_info):
        self.active_row = row_info

    def on_currency_changed(self, row_info):
        self.active_row = row_info
        code = self.code_from_label(row_info["currency_var"].get())
        row_info["currency_var"].set(self.label_for(code))
        self.recalculate_from_active()

    def normalize_currency_selection(self, row_info):
        code = self.code_from_label(row_info["currency_var"].get())
        row_info["currency_var"].set(self.label_for(code))

    def on_amount_changed(self, row_info):
        if self.is_updating:
            return
        self.active_row = row_info
        self.recalculate_from_active()

    def recalculate_from_active(self):
        if self.is_updating or not self.amount_rows:
            return

        source = self.active_row or self.amount_rows[0]
        source_text = source["amount_var"].get().strip().replace(",", "")
        if source_text in {"", ".", "-", "-."}:
            return
        try:
            source_amount = float(source_text)
        except ValueError:
            return

        source_code = self.code_from_label(source["currency_var"].get())
        source_rate = self.rates().get(source_code, 1.0)
        amount_in_cny = source_amount * source_rate

        self.is_updating = True
        try:
            for row in self.amount_rows:
                if row is source:
                    continue
                target_code = self.code_from_label(row["currency_var"].get())
                target_rate = self.rates().get(target_code, 1.0)
                row["amount_var"].set(self.format_amount(amount_in_cny / target_rate))
        finally:
            self.is_updating = False

        self.update_rate_info(source_code, source_amount, amount_in_cny)

    def update_rate_info(self, source_code=None, source_amount=None, amount_in_cny=None):
        if source_code is None:
            self.rate_info_var.set("")
            return
        source_name = self.store.currency_names.get(source_code, source_code)
        mode_label = RATE_MODES[self.rate_mode]
        source_note = "（参考汇率，非中行牌价）" if source_code in self.store.reference_codes else ""
        self.rate_info_var.set(
            f"当前口径：{mode_label}\n"
            f"当前基准：{self.format_amount(source_amount)} {source_name}{source_note} = "
            f"{self.format_amount(amount_in_cny)} 人民币\n"
            f"中行覆盖币种使用中国银行牌价；中行未覆盖币种使用免费参考汇率补齐。"
        )

    def update_status(self, message=None):
        if message:
            self.status_var.set(message)
            return
        updated = self.store.last_update or "未联网更新"
        pub_time = self.store.pub_time or "暂无发布时间"
        self.status_var.set(
            f"汇率来源：{self.store.source}；中行发布时间：{pub_time}；缓存日期：{updated}。"
            f" 当前默认适合外贸出口收汇：现汇买入价。中行未覆盖币种会标记为参考。"
        )

    def refresh_rates_if_needed(self, force=False):
        if not force and not self.store.needs_update():
            self.update_status()
            return

        self.update_status("正在联网获取中国银行外汇牌价...")
        thread = threading.Thread(target=self._refresh_rates_worker, daemon=True)
        thread.start()

    def _refresh_rates_worker(self):
        try:
            self.store.update_from_network()
        except (urllib.error.URLError, TimeoutError, RuntimeError, OSError, json.JSONDecodeError) as error:
            self.after(0, lambda: self.update_status(f"中行牌价联网更新失败，继续使用{self.store.source}。原因：{error}"))
            return
        self.after(0, self.after_rates_updated)

    def after_rates_updated(self):
        self.refresh_currency_options()
        self.recalculate_from_active()
        self.update_status(f"中行牌价已更新：{datetime.now().strftime('%Y-%m-%d %H:%M')}；页面发布时间：{self.store.pub_time}。")

    @staticmethod
    def format_amount(value):
        if abs(value) >= 100000:
            return f"{value:.2f}"
        if abs(value) >= 1:
            return f"{value:.4f}".rstrip("0").rstrip(".")
        return f"{value:.8f}".rstrip("0").rstrip(".")


if __name__ == "__main__":
    app = CurrencyConverterApp()
    app.mainloop()

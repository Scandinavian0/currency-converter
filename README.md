# 实时货币等值转换工具

这是一个只依赖 Python 标准库的桌面小工具，使用 `tkinter` 实现，支持 Windows 和 macOS 源码运行。Windows 可通过 GitHub Actions 自动打包为 `.exe`。

## 本地运行

Windows:

```powershell
py currency_converter.py
```

macOS:

```bash
python3 currency_converter.py
```

## 打包并发布 Windows EXE

项目已配置 GitHub Actions：`.github/workflows/release.yml`。

创建并推送版本标签后，GitHub 会自动打包 `.exe` 并上传到 Releases：

```powershell
git tag v1.0.0
git push origin v1.0.0
```

完成后打开仓库右侧的 `Releases` 页面，即可下载 `currency-converter.exe`。

也可以进入 GitHub 仓库的 `Actions` 页面，选择 `Build Windows EXE`，点击 `Run workflow` 手动打包。手动运行时文件会出现在本次 workflow 的 `Artifacts` 里，不会自动创建 Release。

## 外贸默认口径

程序默认使用中国银行外汇牌价，并默认选择：

```text
出口收汇（现汇买入价）
```

这个口径适合外贸出口收美元、欧元等外币后结汇成人民币的估算。因为银行买入你的外币时，通常参考现汇买入价。

## 可切换口径

- 出口收汇（现汇买入价）
- 进口付款（现汇卖出价）
- 中间价（参考/记账）
- 现钞买入价
- 现钞卖出价

中国银行页面的牌价单位是 `100 外币 = 多少人民币`，程序内部会自动换算成 `1 外币 = 多少人民币`。

## 功能

- 默认提供人民币和美元两个金额输入框。
- 修改任意一个金额，其它金额会按当前口径实时变化。
- 每个金额输入框右侧有删除按钮，至少会保留一个输入框。
- 点击“添加金额输入框”可以增加更多换算行。
- 下方提供独立搜索框，可输入中文名称或币种代码快速定位币种。
- 中国银行覆盖的币种使用中行牌价；中行没有覆盖的币种会用免费参考汇率补齐，并在列表中标记为“参考”。
- 程序会记住关闭前展示过的币种行；下次打开保留这些行，金额归零。
- 点击“重置”会清除展示状态，下次打开恢复默认人民币/美元初始化。
- 启动时每天最多联网比对一次中国银行外汇牌价。
- 当窗口内容显示不完时，右侧会出现滚动条。

## 本地缓存

汇率缓存默认保存在用户目录：

```text
~/.currency_converter_rates.json
```

展示状态默认保存在用户目录：

```text
~/.currency_converter_state.json
```

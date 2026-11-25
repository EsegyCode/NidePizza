# NidePizza (Українська коротко)

Flask-платформа e-commerce для піци та суші: каталог, кошик, оформлення замовлення, оплата Mollie або fallback, повідомлення в Telegram, доставка по кількох містах Нідерландів, SEO/GEO, JSON-LD, llms.txt, sitemap і динамічні OG-зображення.

## Запуск

```powershell
uv venv .venv
uv pip install --python .venv\Scripts\python.exe -r requirements.txt
copy .env.example .env
.venv\Scripts\python.exe run.py
```

Локальний сервер: `http://localhost:8000`. Тести: `.venv\Scripts\pytest.exe -v`.

## Документація

- [English README](README.md)
- [Docs](docs/FEATURES.md)
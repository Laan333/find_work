"""
hh.ru - поиск вакансий Python удалёнка
Без авторизации, только публичный API
"""

import requests
import json
from datetime import datetime

# ── Настройки поиска ──────────────────────────────────────────────────────────
SEARCH_QUERY = "Python"          # Ключевое слово
AREA = 113                        # 113 = Россия, 1 = Москва, 2 = СПб
SCHEDULE = "remote"               # remote = удалёнка
PER_PAGE = 20                     # Вакансий за раз (макс 100)
PAGES = 3                         # Сколько страниц парсить
SALARY_FROM = None                # Минимальная зп (None = без фильтра)
CURRENCY = "RUR"
# ─────────────────────────────────────────────────────────────────────────────

BASE_URL = "https://api.hh.ru"
HEADERS = {"User-Agent": "hh-vacancy-searcher/1.0"}


def search_vacancies(query, area, schedule, salary_from, page):
    params = {
        "text": query,
        "area": area,
        "schedule": schedule,
        "per_page": PER_PAGE,
        "page": page,
        "order_by": "publication_time",  # Свежие первыми
    }
    if salary_from:
        params["salary"] = salary_from
        params["currency"] = CURRENCY
        params["only_with_salary"] = True

    resp = requests.get(f"{BASE_URL}/vacancies", headers=HEADERS, params=params)
    resp.raise_for_status()
    return resp.json()


def get_vacancy_detail(vacancy_id):
    """Получить полное описание вакансии (с требованиями)"""
    resp = requests.get(f"{BASE_URL}/vacancies/{vacancy_id}", headers=HEADERS)
    resp.raise_for_status()
    return resp.json()


def format_salary(salary):
    if not salary:
        return "не указана"
    parts = []
    if salary.get("from"):
        parts.append(f"от {salary['from']:,}")
    if salary.get("to"):
        parts.append(f"до {salary['to']:,}")
    currency = salary.get("currency", "")
    return f"{' '.join(parts)} {currency}".strip()


def print_vacancy(v, index):
    salary = format_salary(v.get("salary"))
    employer = v.get("employer", {}).get("name", "Неизвестно")
    url = v.get("alternate_url", "")
    published = v.get("published_at", "")[:10]

    # Коротко о требованиях из сниппета
    snippet = v.get("snippet", {})
    requirement = snippet.get("requirement", "") or ""
    requirement = requirement.replace("<highlighttext>", "").replace("</highlighttext>", "")

    print(f"\n{'─'*60}")
    print(f"[{index}] {v['name']}")
    print(f"    🏢 {employer}")
    print(f"    💰 {salary}")
    print(f"    📅 {published}")
    print(f"    🔗 {url}")
    if requirement:
        print(f"    📋 {requirement[:150]}...")


def save_to_json(vacancies, filename=None):
    if not filename:
        filename = f"vacancies_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(vacancies, f, ensure_ascii=False, indent=2)
    print(f"\n✅ Сохранено {len(vacancies)} вакансий в {filename}")
    return filename


def main():
    print(f"🔍 Ищу: '{SEARCH_QUERY}' | удалёнка | {'зп от ' + str(SALARY_FROM) if SALARY_FROM else 'любая зп'}")
    print(f"    Регион: {AREA} | Страниц: {PAGES}\n")

    all_vacancies = []
    seen_ids = set()

    for page in range(PAGES):
        print(f"Страница {page + 1}/{PAGES}...", end=" ")
        try:
            data = search_vacancies(SEARCH_QUERY, AREA, SCHEDULE, SALARY_FROM, page)
        except requests.HTTPError as e:
            print(f"Ошибка: {e}")
            break

        items = data.get("items", [])
        total = data.get("found", 0)

        if page == 0:
            print(f"Всего найдено: {total} вакансий")

        new_count = 0
        for v in items:
            if v["id"] not in seen_ids:
                seen_ids.add(v["id"])
                all_vacancies.append(v)
                new_count += 1

        print(f"Добавлено: {new_count}")

        # Если страниц меньше чем запрошено
        if page >= data.get("pages", 0) - 1:
            break

    # Вывод результатов
    print(f"\n{'═'*60}")
    print(f"Итого уникальных вакансий: {len(all_vacancies)}")

    for i, v in enumerate(all_vacancies, 1):
        print_vacancy(v, i)

    # Сохранение
    save_to_json(all_vacancies)

    return all_vacancies


if __name__ == "__main__":
    main()
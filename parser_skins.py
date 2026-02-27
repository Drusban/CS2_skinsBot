import requests
import json
import asyncio
from typing import List, Dict, Optional
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SkinParser:
    def __init__(self):
        self.base_url = "https://api.skinport.com/v1/items"
        self.items_per_page = 10  # Меняем на 10 как в твоем коде
        self.all_skins = []

    async def fetch_skins(self, app_id: int = 730, currency: str = "EUR") -> List[Dict]:
        """
        Получение всех скинов с Skinport API
        """
        try:
            params = {
                'app_id': app_id,
                'currency': currency,
                'tradable': 0  # 0 - все предметы
            }

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            logger.info("Запрашиваем данные с Skinport API...")
            response = requests.get(self.base_url, params=params, headers=headers)
            response.raise_for_status()

            data = response.json()
            logger.info(f"Получено {len(data)} скинов")

            # Обрабатываем и фильтруем данные
            self.all_skins = []
            for item in data:
                # Пропускаем предметы без цены
                if not item.get('min_price') and not item.get('suggested_price'):
                    continue

                # Безопасное получение значений с проверкой на None
                min_price = item.get('min_price')
                if min_price is None:
                    min_price = 0

                suggested_price = item.get('suggested_price')
                if suggested_price is None:
                    suggested_price = 0

                max_price = item.get('max_price')
                if max_price is None:
                    max_price = 0

                mean_price = item.get('mean_price')
                if mean_price is None:
                    mean_price = 0

                median_price = item.get('median_price')
                if median_price is None:
                    median_price = 0

                quantity = item.get('quantity')
                if quantity is None:
                    quantity = 0

                created_at = item.get('created_at')
                if created_at is None:
                    created_at = 0

                updated_at = item.get('updated_at')
                if updated_at is None:
                    updated_at = 0

                processed_item = {
                    'market_hash_name': item.get('market_hash_name', 'Unknown'),
                    'currency': item.get('currency', 'EUR'),
                    'min_price': float(min_price) if min_price else 0,
                    'suggested_price': float(suggested_price) if suggested_price else 0,
                    'max_price': float(max_price) if max_price else 0,
                    'mean_price': float(mean_price) if mean_price else 0,
                    'median_price': float(median_price) if median_price else 0,
                    'quantity': int(quantity) if quantity else 0,
                    'item_page': item.get('item_page', ''),
                    'market_page': item.get('market_page', ''),
                    'created_at': int(created_at) if created_at else 0,
                    'updated_at': int(updated_at) if updated_at else 0
                }
                self.all_skins.append(processed_item)

            # Сортируем по цене (от меньшей к большей) с проверкой на None
            self.all_skins.sort(
                key=lambda x: x['min_price'] if x['min_price'] is not None and x['min_price'] > 0 else float('inf'))

            # Сохраняем в файл для кэша
            self._save_to_cache()

            logger.info(f"Обработано {len(self.all_skins)} скинов")
            return self.all_skins

        except requests.RequestException as e:
            logger.error(f"Ошибка при запросе к API: {e}")
            # Пробуем загрузить из кэша
            return self._load_from_cache()
        except Exception as e:
            logger.error(f"Неожиданная ошибка: {e}")
            return []

    def _save_to_cache(self):
        """Сохранение данных в кэш"""
        try:
            with open('skins_cache.json', 'w', encoding='utf-8') as f:
                json.dump({
                    'timestamp': datetime.now().isoformat(),
                    'skins': self.all_skins
                }, f, indent=2, ensure_ascii=False)
            logger.info("Данные сохранены в кэш")
        except Exception as e:
            logger.error(f"Ошибка при сохранении кэша: {e}")

    def _load_from_cache(self) -> List[Dict]:
        """Загрузка данных из кэша"""
        try:
            with open('skins_cache.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.all_skins = data.get('skins', [])
                logger.info(f"Загружено {len(self.all_skins)} скинов из кэша от {data.get('timestamp')}")
                return self.all_skins
        except FileNotFoundError:
            logger.warning("Кэш не найден")
            return []
        except Exception as e:
            logger.error(f"Ошибка при загрузке кэша: {e}")
            return []

    def get_page(self, page: int = 0) -> List[Dict]:
        """
        Получение одной страницы со скинами
        """
        if not self.all_skins:
            return []

        start = page * self.items_per_page
        end = start + self.items_per_page

        return self.all_skins[start:end]

    def get_batch(self, start_index: int, batch_size: int = 10) -> List[Dict]:
        """
        Получение партии скинов начиная с определенного индекса
        """
        if not self.all_skins:
            return []

        end_index = min(start_index + batch_size, len(self.all_skins))
        return self.all_skins[start_index:end_index]

    def get_total_pages(self) -> int:
        """Получение общего количества страниц"""
        return (len(self.all_skins) + self.items_per_page - 1) // self.items_per_page

    def get_total_count(self) -> int:
        """Получение общего количества скинов"""
        return len(self.all_skins)

    def search_skins(self, query: str) -> List[Dict]:
        """
        Поиск скинов по названию
        """
        query = query.lower()
        results = []

        for skin in self.all_skins:
            if query in skin['market_hash_name'].lower():
                results.append(skin)

        return results

    def filter_by_price(self, min_price: float = 0, max_price: float = float('inf')) -> List[Dict]:
        """
        Фильтрация скинов по цене
        """
        return [
            skin for skin in self.all_skins
            if skin['min_price'] is not None and min_price <= skin['min_price'] <= max_price
        ]

    def get_skin_by_index(self, index: int) -> Optional[Dict]:
        """
        Получение скина по индексу
        """
        if 0 <= index < len(self.all_skins):
            return self.all_skins[index]
        return None


# Создаем глобальный экземпляр парсера
parser = SkinParser()
import pytest
import json
import base64
from unittest.mock import AsyncMock, MagicMock, patch, call

from langchain_core.messages import HumanMessage

from ai_agent import FoodAnalysisService
from apps.food_diary.schemas import DishCreateIn


class TestFoodAnalysisService:
    """Юнит-тесты для FoodAnalysisService"""

    @pytest.fixture
    def mock_llm_client(self):
        """Создает мок LLM клиента"""
        mock_client = AsyncMock()
        mock_client.ainvoke.return_value = MagicMock(content="")
        return mock_client

    @pytest.fixture
    def service(self, mock_llm_client):
        """Создает сервис с замоканным клиентом"""
        with patch("ai_agent.client.LLMClient") as MockLLMClient:
            MockLLMClient.create_client.return_value = mock_llm_client
            service = FoodAnalysisService()
            service._client = mock_llm_client  # явно подменяем клиента
            return service

    @pytest.fixture
    def sample_image_bytes(self):
        """Возвращает тестовые байты изображения"""
        return b"fake_image_bytes_12345"

    @pytest.fixture
    def sample_image_base64(self):
        """Возвращает тестовую base64 строку"""
        return base64.b64encode(b"fake_image_bytes_12345").decode("utf-8")

    @pytest.fixture
    def sample_image_url(self):
        """Возвращает тестовый URL изображения"""
        return "https://example.com/food.jpg"

    @pytest.fixture
    def valid_json_response(self):
        """Возвращает валидный JSON ответ от LLM"""
        return json.dumps(
            [
                {
                    "name": "Овсянка с ягодами",
                    "weight": 250,
                    "calories": 350,
                    "protein": 12.5,
                    "fat": 6.2,
                    "carbohydrates": 60.1,
                },
                {
                    "name": "Банан",
                    "weight": 120,
                    "calories": 105,
                    "protein": 1.3,
                    "fat": 0.4,
                    "carbohydrates": 27.0,
                },
            ]
        )

    @pytest.fixture
    def single_dish_json_response(self):
        """Возвращает JSON с одним блюдом"""
        return json.dumps(
            [
                {
                    "name": "Яблоко",
                    "weight": 180,
                    "calories": 95,
                    "protein": 0.5,
                    "fat": 0.3,
                    "carbohydrates": 25.0,
                }
            ]
        )

    @pytest.fixture
    def invalid_json_response(self):
        """Возвращает невалидный JSON"""
        return "Это просто текст, а не JSON"

    @pytest.fixture
    def json_with_extra_text(self):
        """Возвращает JSON с дополнительным текстом"""
        return """
        Я вижу на фото следующие блюда:
        [
            {
                "name": "Омлет",
                "weight": 200,
                "calories": 350,
                "protein": 20,
                "fat": 25,
                "carbohydrates": 5
            }
        ]
        Надеюсь, это поможет!
        """

    @pytest.fixture
    def single_object_json(self):
        """Возвращает JSON с одним объектом вместо массива"""
        return """
        {
            "name": "Суп",
            "weight": 300,
            "calories": 250,
            "protein": 10,
            "fat": 8,
            "carbohydrates": 30
        }
        """

    # MARK: - Тесты инициализации

    def test_init_with_custom_client(self):
        """Тест инициализации с переданным клиентом"""
        mock_client = MagicMock()
        service = FoodAnalysisService(llm_client=mock_client)

        assert service._client == mock_client

    def test_init_without_client(self):
        """Тест инициализации без клиента (создается автоматически)"""
        with patch("ai_agent.client.LLMClient.create_client") as mock_create:
            mock_client = MagicMock()
            mock_create.return_value = mock_client

            service = FoodAnalysisService()

            mock_create.assert_called_once()
            assert service._client == mock_client

    # MARK: - Тесты analyze_food_image

    @pytest.mark.asyncio
    async def test_analyze_food_image_success_with_bytes(
        self, service, mock_llm_client, sample_image_bytes, valid_json_response
    ):
        """Тест успешного анализа изображения (байты)"""
        mock_llm_client.ainvoke.return_value.content = valid_json_response

        result = await service.analyze_food_image(sample_image_bytes)

        assert len(result) == 2
        assert isinstance(result[0], DishCreateIn)
        assert result[0].name == "Овсянка с ягодами"
        assert result[0].calories == 350
        assert result[0].weight == 250
        assert result[0].protein == 12.5
        assert result[0].fat == 6.2
        assert result[0].carbohydrates == 60.1

        assert result[1].name == "Банан"
        assert result[1].calories == 105

        # Проверяем вызов клиента
        mock_llm_client.ainvoke.assert_called_once()
        args = mock_llm_client.ainvoke.call_args[0][0]
        assert len(args) == 1
        assert isinstance(args[0], HumanMessage)

    @pytest.mark.asyncio
    async def test_analyze_food_image_success_with_url(
        self, service, mock_llm_client, sample_image_url, valid_json_response
    ):
        """Тест успешного анализа изображения (URL)"""
        mock_llm_client.ainvoke.return_value.content = valid_json_response

        result = await service.analyze_food_image(sample_image_url)

        assert len(result) == 2
        assert result[0].name == "Овсянка с ягодами"

        # Проверяем что URL использовался напрямую, а не base64
        mock_llm_client.ainvoke.assert_called_once()

    @pytest.mark.asyncio
    async def test_analyze_food_image_single_dish(
        self, service, mock_llm_client, sample_image_bytes, single_dish_json_response
    ):
        """Тест анализа изображения с одним блюдом"""
        mock_llm_client.ainvoke.return_value.content = single_dish_json_response

        result = await service.analyze_food_image(sample_image_bytes)

        assert len(result) == 1
        assert result[0].name == "Яблоко"
        assert result[0].weight == 180
        assert result[0].calories == 95

    @pytest.mark.asyncio
    async def test_analyze_food_image_empty_response(
        self, service, mock_llm_client, sample_image_bytes
    ):
        """Тест обработки пустого ответа от LLM"""
        mock_llm_client.ainvoke.return_value.content = json.dumps([])

        result = await service.analyze_food_image(sample_image_bytes)

        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_analyze_food_image_invalid_json(
        self, service, mock_llm_client, sample_image_bytes, invalid_json_response
    ):
        """Тест обработки невалидного JSON"""
        mock_llm_client.ainvoke.return_value.content = invalid_json_response

        result = await service.analyze_food_image(sample_image_bytes)

        assert len(result) == 1
        assert result[0].name == "Не удалось распознать"
        assert result[0].weight == 0
        assert result[0].calories == 0
        assert result[0].protein == 0
        assert result[0].fat == 0
        assert result[0].carbohydrates == 0

    @pytest.mark.asyncio
    async def test_analyze_food_image_api_error(
        self, service, mock_llm_client, sample_image_bytes
    ):
        """Тест обработки ошибки от API"""
        mock_llm_client.ainvoke.side_effect = Exception("Connection error")

        with pytest.raises(Exception) as exc_info:
            await service.analyze_food_image(sample_image_bytes)

        assert "Connection error" in str(exc_info.value)

    # MARK: - Тесты _ainvoke_for_chat_open_ai_with_images

    @pytest.mark.asyncio
    async def test_ainvoke_with_images_bytes(
        self, service, mock_llm_client, sample_image_bytes, valid_json_response
    ):
        """Тест отправки изображений (байты)"""
        mock_llm_client.ainvoke.return_value.content = valid_json_response

        result = await service._ainvoke_for_chat_open_ai_with_images(
            [sample_image_bytes]
        )

        assert result == valid_json_response
        mock_llm_client.ainvoke.assert_called_once()

    @pytest.mark.asyncio
    async def test_ainvoke_with_images_url(
        self, service, mock_llm_client, sample_image_url, valid_json_response
    ):
        """Тест отправки изображений (URL)"""
        mock_llm_client.ainvoke.return_value.content = valid_json_response

        result = await service._ainvoke_for_chat_open_ai_with_images([sample_image_url])

        assert result == valid_json_response
        mock_llm_client.ainvoke.assert_called_once()

    @pytest.mark.asyncio
    async def test_ainvoke_with_multiple_images(
        self,
        service,
        mock_llm_client,
        sample_image_bytes,
        sample_image_url,
        valid_json_response,
    ):
        """Тест отправки нескольких изображений"""
        mock_llm_client.ainvoke.return_value.content = valid_json_response

        result = await service._ainvoke_for_chat_open_ai_with_images(
            [sample_image_bytes, sample_image_url]
        )

        assert result == valid_json_response
        mock_llm_client.ainvoke.assert_called_once()

    # MARK: - Тесты _content_for_openai_deepseek

    def test_content_for_openai_deepseek_bytes(
        self, service, sample_image_bytes, sample_image_base64
    ):
        """Тест формирования контента для байтов"""
        content = service._content_for_openai_deepseek([sample_image_bytes])

        assert len(content) == 2  # текст + 1 изображение
        assert content[0]["type"] == "text"
        assert content[0]["text"] == service.prompt
        assert content[1]["type"] == "image_url"
        assert (
            f"data:image/jpeg;base64,{sample_image_base64}"
            in content[1]["image_url"]["url"]
        )

    def test_content_for_openai_deepseek_url(self, service, sample_image_url):
        """Тест формирования контента для URL"""
        content = service._content_for_openai_deepseek([sample_image_url])

        assert len(content) == 2
        assert content[0]["type"] == "text"
        assert content[1]["type"] == "image_url"
        assert content[1]["image_url"]["url"] == sample_image_url

    def test_content_for_openai_deepseek_mixed(
        self, service, sample_image_bytes, sample_image_url
    ):
        """Тест формирования контента для смешанных типов"""
        content = service._content_for_openai_deepseek(
            [sample_image_bytes, sample_image_url]
        )

        assert len(content) == 3  # текст + 2 изображения
        assert content[1]["type"] == "image_url"
        assert "data:image/jpeg;base64" in content[1]["image_url"]["url"]
        assert content[2]["type"] == "image_url"
        assert content[2]["image_url"]["url"] == sample_image_url

    def test_content_for_openai_deepseek_base64_string(
        self, service, sample_image_base64
    ):
        """Тест формирования контента для base64 строки"""
        content = service._content_for_openai_deepseek([sample_image_base64])

        assert len(content) == 2
        assert "data:image/jpeg;base64" in content[1]["image_url"]["url"]
        assert sample_image_base64 in content[1]["image_url"]["url"]

    # MARK: - Тесты analyze_multiple_food_images

    @pytest.mark.asyncio
    async def test_analyze_multiple_food_images_success(
        self, service, mock_llm_client, sample_image_bytes
    ):
        """Тест успешного анализа нескольких изображений"""
        responses = [
            json.dumps(
                [
                    {
                        "name": "Блюдо1",
                        "weight": 100,
                        "calories": 200,
                        "protein": 10,
                        "fat": 5,
                        "carbohydrates": 20,
                    }
                ]
            ),
            json.dumps(
                [
                    {
                        "name": "Блюдо2",
                        "weight": 150,
                        "calories": 300,
                        "protein": 15,
                        "fat": 8,
                        "carbohydrates": 30,
                    }
                ]
            ),
        ]

        # Настраиваем мок для последовательных вызовов
        mock_llm_client.ainvoke.side_effect = [
            MagicMock(content=responses[0]),
            MagicMock(content=responses[1]),
        ]

        images = [sample_image_bytes, sample_image_bytes]
        results = await service.analyze_multiple_food_images(images)

        assert len(results) == 2
        assert results[0].name == "Блюдо1"
        assert results[1].name == "Блюдо2"
        assert mock_llm_client.ainvoke.call_count == 2

    @pytest.mark.asyncio
    async def test_analyze_multiple_food_images_partial_failure(
        self, service, mock_llm_client, sample_image_bytes
    ):
        """Тест анализа нескольких изображений с частичными ошибками"""
        # Первый вызов успешен, второй - ошибка
        mock_llm_client.ainvoke.side_effect = [
            MagicMock(
                content=json.dumps(
                    [
                        {
                            "name": "Блюдо1",
                            "weight": 100,
                            "calories": 200,
                            "protein": 10,
                            "fat": 5,
                            "carbohydrates": 20,
                        }
                    ]
                )
            ),
            Exception("API error"),
        ]

        images = [sample_image_bytes, sample_image_bytes]
        results = await service.analyze_multiple_food_images(images)

        assert len(results) == 2
        assert results[0].name == "Блюдо1"
        assert results[1].name == "Ошибка анализа 2"
        assert results[1].weight == 0
        assert results[1].calories == 0

    @pytest.mark.asyncio
    async def test_analyze_multiple_food_images_all_fail(
        self, service, mock_llm_client, sample_image_bytes
    ):
        """Тест анализа нескольких изображений с полным провалом"""
        mock_llm_client.ainvoke.side_effect = Exception("API error")

        images = [sample_image_bytes, sample_image_bytes]
        results = await service.analyze_multiple_food_images(images)

        assert len(results) == 2
        assert results[0].name == "Ошибка анализа 1"
        assert results[1].name == "Ошибка анализа 2"
        assert results[0].weight == 0
        assert results[1].calories == 0

    @pytest.mark.asyncio
    async def test_analyze_multiple_food_images_empty_list(self, service):
        """Тест анализа пустого списка изображений"""
        results = await service.analyze_multiple_food_images([])

        assert len(results) == 0

    # MARK: - Тесты _extract_json_from_response

    def test_extract_json_from_response_valid_array(self, service, valid_json_response):
        """Тест извлечения валидного JSON массива"""
        result = service._extract_json_from_response(valid_json_response)

        assert len(result) == 2
        assert result[0]["name"] == "Овсянка с ягодами"
        assert result[0]["calories"] == 350

    def test_extract_json_from_response_with_extra_text(
        self, service, json_with_extra_text
    ):
        """Тест извлечения JSON из текста с дополнительным содержимым"""
        result = service._extract_json_from_response(json_with_extra_text)

        assert len(result) == 1
        assert result[0]["name"] == "Омлет"
        assert result[0]["calories"] == 350

    def test_extract_json_from_response_single_object(
        self, service, single_object_json
    ):
        """Тест извлечения JSON с одним объектом (не массивом)"""
        result = service._extract_json_from_response(single_object_json)

        assert len(result) == 1
        assert result[0]["name"] == "Суп"
        assert result[0]["calories"] == 250

    def test_extract_json_from_response_invalid(self, service, invalid_json_response):
        """Тест извлечения из невалидного JSON"""
        result = service._extract_json_from_response(invalid_json_response)

        assert len(result) == 1
        assert result[0]["name"] == "Не удалось распознать"
        assert result[0]["weight"] == 0
        assert result[0]["calories"] == 0

    def test_extract_json_from_response_empty(self, service):
        """Тест извлечения из пустого ответа"""
        result = service._extract_json_from_response("")

        assert len(result) == 1
        assert result[0]["name"] == "Не удалось распознать"

    # MARK: - Интеграционные тесты методов

    @pytest.mark.asyncio
    async def test_full_analysis_flow(
        self, service, mock_llm_client, sample_image_bytes, json_with_extra_text
    ):
        """Тест полного потока анализа"""
        mock_llm_client.ainvoke.return_value.content = json_with_extra_text

        result = await service.analyze_food_image(sample_image_bytes)

        assert len(result) == 1
        assert result[0].name == "Омлет"
        assert result[0].weight == 200
        assert result[0].calories == 350
        assert result[0].protein == 20
        assert result[0].fat == 25
        assert result[0].carbohydrates == 5

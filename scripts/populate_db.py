# scripts/populate_db.py
# !/usr/bin/env python
import os
import sys
import django
import random
from datetime import date, time, timedelta

# Настраиваем Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.accounts.models import User, PatientProfile
from apps.food_diary.models import Meal, Dish, MealTimeSlot


def create_users():
    """Создать тестовых пользователей"""
    print("Создаем пользователей...")

    # Создаем пользователя
    user, created = User.objects.get_or_create(
        email="patient@test.com",
        defaults={
            "username": "test_patient",
            "is_patient": True
        }
    )
    if created:
        user.set_password("testpass123")
        user.save()
        print(f"  Создан пользователь: {user.email}")

    # Создаем профиль пациента
    patient, created = PatientProfile.objects.get_or_create(
        user=user,
        defaults={
            "birth_date": date(1990, 1, 1),
            "height": 175.0,
            "weight": 70.0,
            "personal_info": {
                "first_name": "Тест",
                "last_name": "Пациентов",
                "gender": "male"
            }
        }
    )
    if created:
        print(f"  Создан профиль пациента: {patient.id}")

    return patient


def create_meal_time_slots():
    """Создать интервалы времени для приемов пищи"""
    print("\nСоздаем интервалы времени...")

    slots_data = [
        {"title": "breakfast", "start_hour": 6, "end_hour": 10},
        {"title": "lunch", "start_hour": 12, "end_hour": 15},
        {"title": "dinner", "start_hour": 18, "end_hour": 21},
        {"title": "snack", "start_hour": 10, "end_hour": 23},
    ]

    for slot_data in slots_data:
        slot, created = MealTimeSlot.objects.get_or_create(
            title=slot_data["title"],
            defaults={
                "start_hour": slot_data["start_hour"],
                "end_hour": slot_data["end_hour"]
            }
        )
        if created:
            print(f"  Создан слот: {slot.get_title_display()}")

    return MealTimeSlot.objects.all()


def create_sample_dishes():
    """Создать примеры блюд"""
    return [
        {
            "name": "Омлет с сыром",
            "weight": 200,
            "calories": 350,
            "protein": 20,
            "fat": 25,
            "carbohydrates": 5,
            "score": 0.8,
            "description": "Омлет из 3 яиц с сыром"
        },
        {
            "name": "Гречка с курицей",
            "weight": 300,
            "calories": 400,
            "protein": 30,
            "fat": 10,
            "carbohydrates": 45,
            "score": 0.9,
            "description": "Гречка отварная с куриным филе"
        },
        {
            "name": "Салат Цезарь",
            "weight": 250,
            "calories": 450,
            "protein": 15,
            "fat": 35,
            "carbohydrates": 15,
            "score": 0.6,
            "description": "Салат с курицей и соусом"
        },
        {
            "name": "Яблоко",
            "weight": 150,
            "calories": 80,
            "protein": 0.5,
            "fat": 0.3,
            "carbohydrates": 20,
            "score": 1.0,
            "description": "Свежее яблоко"
        },
        {
            "name": "Йогурт",
            "weight": 150,
            "calories": 120,
            "protein": 5,
            "fat": 3,
            "carbohydrates": 18,
            "score": 0.9,
            "description": "Натуральный йогурт"
        }
    ]


def create_meals(patient, days_back=7):
    """Создать тестовые приемы пищи за последние N дней"""
    print(f"\nСоздаем приемы пищи за последние {days_back} дней...")

    dishes_data = create_sample_dishes()
    meal_types = ['breakfast', 'lunch', 'dinner', 'snack']

    meals_created = 0

    for day in range(days_back):
        current_date = date.today() - timedelta(days=day)

        # Для каждого дня создаем 2-4 приема пищи
        num_meals = random.randint(2, 4)
        selected_types = random.sample(meal_types, num_meals)

        for meal_type in selected_types:
            # Случайное время
            if meal_type == 'breakfast':
                hour = random.randint(7, 9)
            elif meal_type == 'lunch':
                hour = random.randint(12, 14)
            elif meal_type == 'dinner':
                hour = random.randint(18, 20)
            else:  # snack
                hour = random.randint(10, 22)

            minute = random.choice([0, 15, 30, 45])
            meal_time = time(hour, minute)

            # Создаем прием пищи
            meal = Meal.objects.create(
                patient=patient,
                name=meal_type.capitalize(),
                meal_date=current_date,
                meal_time=meal_time,
                portion_size="Стандартная",
                description=f"Прием пищи от {current_date}"
            )

            # Добавляем 1-3 блюда
            num_dishes = random.randint(1, 3)
            selected_dishes = random.sample(dishes_data, num_dishes)

            for dish_data in selected_dishes:
                # Немного варьируем параметры
                dish = Dish.objects.create(
                    meal=meal,
                    name=dish_data["name"],
                    weight=dish_data["weight"] + random.randint(-20, 20),
                    calories=dish_data["calories"] + random.randint(-20, 20),
                    protein=dish_data["protein"] + round(random.uniform(-2, 2), 1),
                    fat=dish_data["fat"] + round(random.uniform(-2, 2), 1),
                    carbohydrates=dish_data["carbohydrates"] + round(random.uniform(-2, 2), 1),
                    score=min(1.0, max(0.0, dish_data["score"] + round(random.uniform(-0.1, 0.1), 2))),
                    description=dish_data["description"]
                )

            meals_created += 1
            if meals_created % 5 == 0:
                print(f"  Создано {meals_created} приемов пищи...")

    print(f"  Всего создано {meals_created} приемов пищи")
    return meals_created


def main():
    """Главная функция"""
    print("=" * 50)
    print("Заполнение базы данных тестовыми данными")
    print("=" * 50)

    # Создаем пользователей
    patient = create_users()

    # Создаем интервалы времени
    create_meal_time_slots()

    # Создаем приемы пищи
    create_meals(patient, days_back=14)

    print("\n" + "=" * 50)
    print("Готово! База данных заполнена.")
    print("=" * 50)
    print("\nТестовый пользователь:")
    print("  Email: patient@test.com")
    print("  Пароль: testpass123")
    print("\nAPI доступно по адресу: http://localhost:8000/api/")
    print("Документация: http://localhost:8000/api/app/v1/docs")
    print("Food эндпоинты: http://localhost:8000/api/food/...")


if __name__ == "__main__":
    main()
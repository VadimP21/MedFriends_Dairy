| Откуда | Куда | Метод |
| :--- | :--- | :--- |
| Django | Pydantic | DishSchema.model_validate(obj) |
| Pydantic | Dict | obj.model_dump() |
| Pydantic | JSON | obj.model_dump_json() |
| Dict | Pydantic | DishSchema.model_validate(dict_data) |
| JSON | Pydantic | DishSchema.model_validate_json(json_str) |
| Pydantic | Django | Dish(**obj.model_dump()) |

| Форма    | Нейминг                                                        |  |
|:---------|:---------------------------------------------------------------| :--- |
| Django   | 'obj' _ model                                                  |  |
| Pydantic | 'obj'                                                          |  |
| List     | 'obj' _ to _ <create, read, ...>                               |  |
| Dict     | 'obj' _ to _ <create, read, ...>                               |  |
| JSON     | 'obj' _ data                                                   |  |
| Pydantic |                                                                |  |


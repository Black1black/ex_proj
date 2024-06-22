from src.databases.redisdb import redis


from src.databases.redisdb import RedisConnect


async def find_in_redis_list(list_name: str, value_to_check: int):
    # Проверка наличия значения в списке с использованием Lua скрипта
    # TODO - лучше в дальнейшем переписать на хэш таблицу чтобы можно было выносить дополнительные данные
    #  (К примеру - локация) и для оптимизации скорости поиска
    script = """
    local list_name = KEYS[1]
    local value_to_check = ARGV[1]

    -- Проверка существования списка
    if redis.call('EXISTS', list_name) == 0 then
        return false
    end

    -- Получение всех элементов списка
    local values = redis.call('LRANGE', list_name, 0, -1)
    for _, value in ipairs(values) do
        if value == value_to_check then
            return true
        end
    end
    return false
    """

    # Выполнение скрипта на стороне Redis (чтобы не передавать целый список на сервер)
    async with RedisConnect().get_redis_client() as client:
        found = await client.eval(script, 1, list_name, value_to_check)

    if found:
        print(f'{value_to_check} В {list_name}')
        return True
    else:
        return False





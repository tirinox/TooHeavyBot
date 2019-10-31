from util.database import DB


async def fix_weight_point():
    # TimePoint:weight:102:2019:10:27 -> WeightPoint:192398802:2019:10:31
    db = DB()

    keys = await db.scan('TimePoint:weight:*')
    for old_key in keys:
        components = old_key.split(':')
        new_components = ['WeightPoint'] + components[2:]
        new_key = ':'.join(new_components)
        print(f'{old_key} -> {new_key}')

        data = await DB().redis.get(old_key)
        await DB().redis.set(new_key, data)
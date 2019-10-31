import sys
from mytools.fix_weight_point import fix_weight_point
import asyncio
from util.database import DB


if __name__ == '__main__':
    if len(sys.argv) <= 2:
        print(f'Usage: python {sys.argv[0]} <config.yml> <command>')
        print('    where command:')
        print('         fixWeightPoint')
    elif len(sys.argv) == 3:

        loop = asyncio.get_event_loop()
        loop.run_until_complete(DB().connect())

        command = sys.argv[2]
        if command == 'fixWeightPoint':
            loop.run_until_complete(fix_weight_point())

import random
import datetime
import asyncio


'''
async def update_password(client):
    await client.wait_until_ready()
    while not client.is_closed():
        try:
            s = "abcdefghijklmnopqrstuvwxyz01234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()?"
            passlen = 22
            now2 = datetime.datetime.now()
            nownow = now2.replace(second=0, microsecond=0)
            future = now2.replace(hour=23, minute=59, second=0, microsecond=0)
            if str(nownow) == str(future):
                print("-Beginning Website Password update")
                pwrd = "".join(random.sample(s, passlen))

                query = "UPDATE WebAuth" \
                        " SET WebPassword =  ?"
                mssql.update(_sql, query, pwrd)
                print("-Website Password update completed *" + pwrd + "*")
                await asyncio.sleep(60)
            else:
                await asyncio.sleep(15)
        except Exception as e:
            print(str(e))
'''
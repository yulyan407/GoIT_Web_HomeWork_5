import platform
import httpx
import asyncio
from datetime import datetime, timedelta
import sys


class HttpError(Exception):
    pass


async def request(url: str):
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        if resp.status_code == 200:
            result = resp.json()
            return result
        else:
            raise HttpError(f'Error status: {resp.status_code} for {url}')


async def main(last_days):
    response_last_days = []
    days = int(last_days)
    if 1 <= days <= 10:
        for days_diff in range(1, days+1):
            date = (datetime.now() - timedelta(days=days_diff)).strftime('%d.%m.%Y')
            try:
                response = await request(f'https://api.privatbank.ua/p24api/exchange_rates?date={date}')
                currency_info = {}
                for currency in response['exchangeRate']:
                    if currency['currency'] in ['EUR', 'USD']:
                        currency_info[currency['currency']] = {
                            'sale': currency.get('saleRate', currency['saleRateNB']),
                            'purchase': currency.get('purchaseRate', currency['purchaseRateNB'])}
                formatted_response = {response['date']: currency_info}
            except HttpError as err:
                print(err)
                response = None
            response_last_days.append(formatted_response)
    else:
        print("Please enter the number of last days between 1 and 10.")
        return None

    return response_last_days


if __name__ == "__main__":
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    result_data = asyncio.run(main(sys.argv[1]))
    print(result_data)

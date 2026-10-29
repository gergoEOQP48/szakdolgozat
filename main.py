import time
import database
import scraper
import notifier
import schedule

def run_price_tracker():

    print("Automatikus árfigyelő futtatás kezdődik...")
    print("1. Adatbázis inicializálása...")
    database.init_db()

    
    product_urls = [
        # Processzorok
        "https://www.arukereso.hu/processzor-c3139/amd/ryzen-7-7800x3d-8-core-4-2ghz-am5-box-100-100000910wof-p948235329/",
        "https://www.arukereso.hu/processzor-c3139/amd/ryzen-7-5800x3d-8-core-3-4ghz-am4-box-100-1000000651wof-p796327434/",
        "https://www.arukereso.hu/processzor-c3139/amd/ryzen-5-9600x-6-core-3-9ghz-am5-box-100-100001405wof-p1115237581/",
        "https://www.arukereso.hu/processzor-c3139/amd/ryzen-7-5700x-8-core-3-4-ghz-am4-box-100-100000926wof-p790043586/",
        "https://www.arukereso.hu/processzor-c3139/amd/ryzen-7-5800x-8-core-3-8ghz-am4-box-100-100000063wof-p602155692/",
        
        # Videókártyák
        "https://www.arukereso.hu/videokartya-c3142/asus/geforce-rtx-5060-dual-oc-8gb-gddr7-128bit-dual-rtx5060-o8g-90yv0n12-m0na00-p1200121441/",
        "https://www.arukereso.hu/videokartya-c3142/sapphire/radeon-rx-9060-xt-pulse-oc-8gb-gddr6-128bit-11350-04-20g-p1204154365/",
        "https://www.arukereso.hu/videokartya-c3142/asus/radeon-rx-9060-xt-dual-16gb-gddr6-128bit-dual-rx9060xt-16g-p1234540687/",
        
        # Memóriák
        "https://www.arukereso.hu/memoria-modul-c3577/kingston/fury-beast-32gb-2x16gb-ddr5-6000mhz-kf560c30bbek2-32-p1062777223/",
        "https://www.arukereso.hu/memoria-modul-c3577/kingston/fury-beast-32gb-2x16gb-ddr4-3200mhz-kf432c16bbk2-32-p690366684/",
        "https://www.arukereso.hu/memoria-modul-c3577/kingston/fury-beast-16gb-2x8gb-ddr5-5600mhz-kf556c40bbk2-16-p778302819/",
    ]

    print(f"Összesen {len(product_urls)} termék feldolgozása következik...\n")

    
    for index, url in enumerate(product_urls, 1):
        print(f"--- [{index}/{len(product_urls)}] Termék feldolgozása ---")
        print(f"URL: {url}")
        
        try:
            
            product_data = scraper.get_arukereso_product(url)

            if product_data:
                print(f"Siker: {product_data['name']} ({product_data['category']})")
                print(f"Talált boltok száma: {len(product_data['offers'])}")

            
                category = product_data['category']
                product_name_upper = product_data['name'].upper()

                if category == 'RAM':
                    if 'DDR4' in product_name_upper:
                        target_price = 45000
                    elif 'DDR5' in product_name_upper:
                        target_price = 250000
                    else:
                        target_price = 50000
                elif category == 'CPU':
                    target_price = 150000
                elif category == 'GPU':
                    target_price = 220000
                else:
                    target_price = 230000

                print(f"Mentés az adatbázisba (célár: {target_price} Ft)...")
                database.save_scraped_data(product_data, target_price=target_price)
                print("Adatok rögzítve.")
            else:
                print("A scraper nem talált feldolgozható adatot ezen az oldalon.")

        except Exception as e:
            print(f" Hiba történt ennél a terméknél: {e}")

        
        if index < len(product_urls):
            print("Várakozás a következő termékre...")
            time.sleep(10)
        
        print("-" * 50)

    print("\nMinden termék lekérdezése és mentése lefutott!")

    print("\n5. Értesítési modul indítása...")
    notifier.check_price_alerts()

def main():

    print("A program a háttérben fut, és minden nap reggel 8:00-kor automatikusan ellenőrzi az árakat.")
    
    schedule.every().day.at("14:00").do(run_price_tracker)
    
    run_price_tracker()

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()

    
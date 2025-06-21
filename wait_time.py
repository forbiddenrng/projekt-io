from random import random, randint
import math

data = [
    [1, "tvn24", "Jeśli ta strona, umownie nazwijmy ją demokratyczna, nie będzie tak zmobilizowana jak w październiku 2023 roku, to Rafał Trzaskowski przegra. Jeśli będziemy tak zmobilizowani jak wtedy, to Rafał Trzaskowski wygra - powiedział w @faktypofaktach premier @donaldtusk.\n\nZobacz całą https://t.co/g274DHo36h", "Thu May 22 18:55:01 +0000 2025", 149, 531, 45288],
    [2, "Rafał Trzaskowski", 'Na moim podwórku w dzieciństwie zwykło się mówić, że "nie ma miękkiej gry". No i wczoraj na SGH miękkiej gry zdecydowanie nie było.\n\nAula Główna pełna młodych ludzi mających swoje przemyślenia, swoje poglądy i całą serię naprawdę ciekawych, wymagających pytań. O gospodarkę. O https://t.co/JQflXKnUvW', "Thu May 22 07:28:48 +0000 2025", 661, 4754, 139198],
    [3, "Dorota Szmal RN🇵🇱", "Policja w uśmiechniętej Polsce Tuska , ściga Zorro z Tarnowa, który wywiesił podczas wiecu Rafała Trzaskowskiego banner na dachu jednej z kamienic. Akcja za zamaskowanym mężczyzną jest prowadzona na szeroką skalę\n#ByleNieTrzaskowski https://t.co/J3JGXozGlR", "Fri May 23 16:30:21 +0000 2025", 16, 202, 11909],
    [4, "Rafał Trzaskowski", "Cieszę się, że minister @JacekSiewiera pozytywnie odpowiedział na moje zaproszenie do współpracy jako społeczny doradca. W sprawach najważniejszych warto sięgać po wsparcie ekspertów z różnych środowisk.\n\nA bezpieczeństwo Polski to zbyt ważna sprawa, żeby co kilka lat robić w https://t.co/5l8nZ2lIfe", "Wed May 21 11:49:29 +0000 2025", 1004, 7252, 595802],
    [5, "Mila", "1.06\nIdź na wybory \nGłosuj na Rafał Trzaskowski❗❗❗\n bo tylko on jest gwarantem normalności i spokojuw kraju \n\nDla tych wszystkich którym spowszedniała normalność przypominam czym są rządy PiS \nGaz i Pała \nTo jest symbol ich rządów \n👇 https://t.co/Rlz0jhdMJG", "Tue May 20 03:20:24 +0000 2025", 227, 789, 17219],
    [6, "Rafał Trzaskowski", "Chcę Polski silnej. Polski ambitnej. Polski, która wszystkim stwarza takie same możliwości. Polski, w której każdy może zrealizować swoje aspiracje. Bo Polska nie jest przeciętna. Polska jest stworzona do wielkości. Czas sięgnąć po naszą szansę.\n\nDziś mamy Roberta Lewandowskiego, https://t.co/CXr0njn7au", "Tue May 20 20:47:53 +0000 2025", 1293, 5529, 206144],
    [7, "Rafał Trzaskowski", "Sosnowiec. Na żywo. Bądźcie z nami. Cała Polska naprzód! #Trzaskowski2025 #WygraCałaPolska https://t.co/oIt7Rds6h8", "Tue May 20 15:00:45 +0000 2025", 215, 1014, 91004],
    [8, "Rafał Trzaskowski", "Dziękuję! ❤️ https://t.co/O2DAOMJzfr", "Fri May 23 20:35:52 +0000 2025", 1414, 17887, 661079],
    [9, "Rafał Trzaskowski", "Wierzchosławice. Jedno z najważniejszych miejsc dla ruchu ludowego, ale też dla wszystkich Polek i Polaków. Dziś oddaliśmy tu hołd Wincentemu Witosowi - historycznemu liderowi PSL i trzykrotnemu premierowi, wspólnie z jego praprawnukiem Wojciechem Steindelem oraz premierem https://t.co/LNmoyNoIqe", "Thu May 22 15:30:50 +0000 2025", 381, 2568, 84041],
    [10, "Mateusz Kurzejewski", "„Cóż szkodzi obiecać…” poseł Witek z PO o podejściu Rafała Trzaskowskiego do postulatów Mentzena 🤦‍♂️ https://t.co/Wan6s9U21t", "Tue May 20 19:54:58 +0000 2025", 49, 1070, 59625],
]

MIN_WAIT_TIME = 15

def get_next_wait_time():
  wait_time = 0
  for tweet in data:
    read_tweet = random() < 0.7
    print(read_tweet)
    if read_tweet:
      text = tweet[2]
      word_count = len(text.split())
      print(word_count)
      wait_time += word_count * 0.3
  random_offset = randint(2, 7)
  print(wait_time)
  return max(int(wait_time), MIN_WAIT_TIME) + random_offset

print(get_next_wait_time())
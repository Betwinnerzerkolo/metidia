#!/usr/bin/env python3
"""
BetScore Casino - Multi-language page builder.
Reads the current French index.html as template, then generates all 6 language versions.
"""
import json, os, re, copy

# ── Load config ──
with open("_lang_config.json") as f:
    CFG = json.load(f)

# ── Read base template (French index.html) ──
with open("index.html") as f:
    BASE_HTML = f.read()

# ── Extra game definitions (games not in the base 29) ──
# Each game needs: slug (for image filename), display_name, provider, category, category_class
# Descriptions are per-language below.
EXTRA_GAME_META = {
    "book-of-ra": {
        "name": "Book of Ra",
        "provider": "Novomatic",
        "category": "Slot",
        "cat_class": "",
        "img": "book-of-ra.webp",
    },
    "4-supercharged-clovers": {
        "name": "4 Supercharged Clovers: Hold and Win",
        "provider": "3 Oaks Gaming",
        "category": "Slot",
        "cat_class": "",
        "img": "4-supercharged-clovers.webp",
    },
    "triple-5s-supercharged": {
        "name": "Triple 5's: Supercharged",
        "provider": "3 Oaks Gaming",
        "category": "Slot",
        "cat_class": "",
        "img": "triple-5s-supercharged.webp",
    },
    "20-boost-hot": {
        "name": "20 Boost Hot",
        "provider": "Fazi",
        "category": "Slot",
        "cat_class": "",
        "img": "20-boost-hot.webp",
    },
    # These 3 already exist in base 29 but need language-specific descriptions for extra copies
    "gates-of-olympus-1000": {
        "name": "Gates of Olympus 1000",
        "provider": "Pragmatic Play",
        "category": "Slot",
        "cat_class": "",
        "img": "gates-of-olympus-1000.webp",
    },
    "40-mega-hotfire": {
        "name": "40 Mega Hotfire",
        "provider": "Fazi",
        "category": "Slot",
        "cat_class": "",
        "img": "40-mega-hotfire.webp",
    },
    "100-golden-coins": {
        "name": "100 Golden Coins: Reel Fishing",
        "provider": "Pragmatic Play",
        "category": "Slot",
        "cat_class": "",
        "img": "100-golden-coins-reel-fishing.webp",
    },
}

# Descriptions per language for extra games
EXTRA_DESCS = {
    "fr": {
        "gates-of-olympus-1000": "Machine a sous divine avec multiplicateurs Zeus et theme Olympe. Rouleaux en cascade avec multiplicateurs jusqu'a 1 000x et tours gratuits bonus.",
        "40-mega-hotfire": "Machine a sous classique aux fruits avec mecaniques de feu. 40 lignes de paiement avec des wilds empiles, des re-spins de feu et des symboles expansifs.",
        "100-golden-coins": "Machine a sous aventure de peche avec collection de pieces d'or. Lancez votre ligne pour des prises bonus avec des re-spins hold and win.",
        "book-of-ra": "Explorez les tombeaux egyptiens pour des tresors caches. Le symbole livre sert de wild et scatter avec tours gratuits et symbole en expansion special.",
        "4-supercharged-clovers": "Machine a sous sur theme irlandais avec trefles porte-bonheur. Mecanique Hold and Win avec re-spins et jackpots progressifs sur 4 niveaux.",
        "triple-5s-supercharged": "Machine a sous retro surpuissante avec symboles 555 classiques. Multiplicateurs empiles et tours gratuits avec wilds collants et re-spins bonus.",
        "20-boost-hot": "Machine a sous chaude avec 20 lignes de paiement et symboles fruits. Fonction boost multiplie les gains avec des tours gratuits et des wilds empiles.",
    },
    "pl": {
        "gates-of-olympus-1000": "Boski slot z mnoznikami Zeusa i tematyke Olimpu. Kaskadowe bebny z mnoznikami do 1 000x i darmowymi spinami bonusowymi.",
        "40-mega-hotfire": "Klasyczny owocowy automat z mechanika ognia. 40 linii wyplat z dzikimi symbolami, ognistymi re-spinami i rozszerzajacymi sie symbolami.",
        "100-golden-coins": "Wedkarski automat z kolekcja zlotych monet. Zarzuc wedke po bonusowe zdobycze z re-spinami hold and win.",
        "book-of-ra": "Odkrywaj egipskie grobowce w poszukiwaniu ukrytych skarbow. Symbol ksiegi pelni funkcje wild i scatter z darmowymi spinami i specjalnym rozszerzajacym sie symbolem.",
        "4-supercharged-clovers": "Automat w irlandzkiej tematyce z szczesliwymi koniczynami. Mechanika Hold and Win z re-spinami i progresywnymi jackpotami na 4 poziomach.",
        "triple-5s-supercharged": "Retro automat z doladowanymi klasycznymi symbolami 555. Mnozniki kumulowane i darmowe spiny z dzikimi symbolami i bonusowymi re-spinami.",
        "20-boost-hot": "Goracy automat z 20 liniami wyplat i owocowymi symbolami. Funkcja boost mnozy wygrane z darmowymi spinami i dzikimi symbolami.",
    },
    "de": {
        "gates-of-olympus-1000": "Gottlicher Slot mit Zeus-Multiplikatoren und Olymp-Thema. Kaskadierende Walzen mit Multiplikatoren bis zu 1.000x und Bonus-Freispielen.",
        "40-mega-hotfire": "Klassischer Frucht-Slot mit Feuer-Mechanik. 40 Gewinnlinien mit gestapelten Wilds, Feuer-Respins und expandierenden Symbolen.",
        "100-golden-coins": "Angel-Abenteuer-Slot mit Goldmunzensammlung. Werfen Sie Ihre Angel fur Bonusfange mit Hold-and-Win-Respins aus.",
        "book-of-ra": "Erkunden Sie agyptische Graber nach verborgenen Schatzen. Das Buchsymbol dient als Wild und Scatter mit Freispielen und speziellem expandierendem Symbol.",
        "4-supercharged-clovers": "Irisch thematisierter Slot mit Gluckskleeblatt. Hold-and-Win-Mechanik mit Respins und progressiven Jackpots auf 4 Ebenen.",
        "triple-5s-supercharged": "Retro-Slot mit aufgeladenen klassischen 555-Symbolen. Gestapelte Multiplikatoren und Freispiele mit klebrigen Wilds und Bonus-Respins.",
        "20-boost-hot": "Heisser Slot mit 20 Gewinnlinien und Fruchtsymbolen. Boost-Funktion multipliziert Gewinne mit Freispielen und gestapelten Wilds.",
    },
    "es": {
        "gates-of-olympus-1000": "Tragamonedas divino con multiplicadores de Zeus y tema del Olimpo. Rodillos en cascada con multiplicadores hasta 1.000x y giros gratis de bonificacion.",
        "40-mega-hotfire": "Tragamonedas clasico de frutas con mecanicas de fuego. 40 lineas de pago con comodines apilados, re-giros de fuego y simbolos expansivos.",
        "100-golden-coins": "Tragamonedas de aventura de pesca con coleccion de monedas de oro. Lanza tu linea para capturas de bonificacion con re-giros hold and win.",
        "book-of-ra": "Explora tumbas egipcias en busca de tesoros ocultos. El simbolo del libro sirve como comodin y scatter con giros gratis y simbolo expansivo especial.",
        "4-supercharged-clovers": "Tragamonedas tematico irlandes con treboles de la suerte. Mecanica Hold and Win con re-giros y jackpots progresivos en 4 niveles.",
        "triple-5s-supercharged": "Tragamonedas retro supercargado con simbolos clasicos 555. Multiplicadores apilados y giros gratis con comodines pegajosos y re-giros de bonificacion.",
        "20-boost-hot": "Tragamonedas caliente con 20 lineas de pago y simbolos de frutas. Funcion boost multiplica ganancias con giros gratis y comodines apilados.",
    },
    "en": {
        "gates-of-olympus-1000": "Divine slot with Zeus multipliers and Olympus theme. Cascading reels with multipliers up to 1,000x and bonus free spins.",
        "40-mega-hotfire": "Classic fruit slot with fire mechanics. 40 paylines with stacked wilds, fire respins and expanding symbols.",
        "100-golden-coins": "Fishing adventure slot with golden coin collection. Cast your line for bonus catches with hold and win respins.",
        "book-of-ra": "Explore Egyptian tombs for hidden treasures. The book symbol serves as both wild and scatter with free spins and special expanding symbol.",
        "4-supercharged-clovers": "Irish-themed slot with lucky clovers. Hold and Win mechanic with respins and progressive jackpots on 4 levels.",
        "triple-5s-supercharged": "Retro supercharged slot with classic 555 symbols. Stacked multipliers and free spins with sticky wilds and bonus respins.",
        "20-boost-hot": "Hot slot with 20 paylines and fruit symbols. Boost feature multiplies wins with free spins and stacked wilds.",
    },
    "pt": {
        "gates-of-olympus-1000": "Slot divino com multiplicadores de Zeus e tema do Olimpo. Rolos em cascata com multiplicadores ate 1.000x e rodadas gratis de bonus.",
        "40-mega-hotfire": "Slot classico de frutas com mecanicas de fogo. 40 linhas de pagamento com wilds empilhados, re-spins de fogo e simbolos expansivos.",
        "100-golden-coins": "Slot de aventura de pesca com colecao de moedas de ouro. Lance sua linha para capturas de bonus com re-spins hold and win.",
        "book-of-ra": "Explore tumbas egipcias em busca de tesouros escondidos. O simbolo do livro serve como wild e scatter com rodadas gratis e simbolo especial expansivo.",
        "4-supercharged-clovers": "Slot com tema irlandes e trevos da sorte. Mecanica Hold and Win com re-spins e jackpots progressivos em 4 niveis.",
        "triple-5s-supercharged": "Slot retro supercarregado com simbolos classicos 555. Multiplicadores empilhados e rodadas gratis com wilds fixos e re-spins de bonus.",
        "20-boost-hot": "Slot quente com 20 linhas de pagamento e simbolos de frutas. Funcao boost multiplica ganhos com rodadas gratis e wilds empilhados.",
    },
}

# ── Translated game descriptions for base 29 games ──
# The base HTML already has French descriptions. For other languages we need full translated game descriptions.
BASE_GAME_DESCS = {
    "pl": [
        "Rundy bonusowe z rozszerzajacymi sie dzikimi symbolami i re-spinami z mnoznikami. Maksymalna wygrana do 5 000x stawki.",
        "Wyplaty klasterowe z kaskadowymi symbolami i darmowymi spinami. Mnozniki rosna z kazda kaskada.",
        "Funkcja bomby usuwa symbole o niskiej wartosci i uruchamia reakcje lancuchowe. Wyplaty o wysokiej zmiennosci.",
        "Zbieraj symbole wedkarza po natychmiastowe nagrody pieniezne. Bonus pilkarski z mechanika Hold and Spin.",
        "Wybierz swoja runde bonusowa: darmowe spiny lub kolo pieniezne. Dzikie smoki mnoza wygrane podczas funkcji.",
        "Lepkie dzikie symbole z kumulowanymi mnoznikami podczas darmowych spinow. Funkcja deszczu dzikich symboli dla wiekszych kombinacji.",
        "Mechanika spadania w stylu Plinko z trzema poziomami potow. Wpadnij do zlotych potow po najwyzsze mnozniki.",
        "Dzikie duchy nawiedzaja bebny przez kilka kolejek. Re-spiny uruchamiane z kazdym wylodowanym symbolem ducha.",
        "Do 117 649 sposobow na wygrana z silnikiem Megaways. Jackpoty smoczych potow dostepne w kazdym obrocie.",
        "Bonus w irlandzkiej tematyce z mnoznikami szczesliwego kamienia. Darmowe spiny z progresywna drabina mnoznikow.",
        "Tajemniczy sklep przyznaje losowe nagrody bonusowe. Wybierz przedmioty po natychmiastowe wygrane lub wejscie do darmowych spinow.",
        "Egipska przygoda z mechanika bonus lamiglow. Odblokuj symbole sejfu po pomnozoone wyplaty.",
        "Kolekcja przekleteych skrzyn uruchamia bonus na trzech poziomach. Kazdy poziom skrzyni zwieksza potencjalne mnozniki.",
        "Automat o wysokiej zmiennosci na pustynnym tle z trwalymi mnoznikami. Popiol zamienia sie w dzikie symbole podczas re-spinow.",
        "Mroczna tematyka dynastii z kumulowaniem symboli smierci. Dostepny zakup bonusu dla bezposredniego dostepu do funkcji.",
        "Przekopuj sie przez warstwy po ukryte mnozniki i nagrody. Kazdy poziom glebokosci zwieksza potencjal nagrod.",
        "Dzikie symbole luzaka rozprzestrzeniaja sie po bebnach podczas darmowych spinow. Rozszerzajacy sie beben dzikich symboli przy aktywacji bonusu.",
        "Ekstremalny poziom zmiennosci z mechanikami xWays i xBet. Wiele poziomow darmowych spinow z rosnacymi mnoznikami.",
        "Mechanika Blitzways z szybkimi transformacjami symboli. Bonus w stylu Dead or Alive z lepkimi dzikimi symbolami.",
        "Bramy mocy otwieraja progresywne poziomy darmowych spinow. Symbole mnoznikow gromadza sie podczas rund bonusowych.",
        "Tajemnicze symbole ujawniaja pasujace ikony dla wiekszych wygranych. Krolewski bonus z pomnozonoymi liniami wyplat.",
        "Ruletka na zywo z mnoznikami spadajacymi pod wplywem grawitacji. Losowe numery otrzymuja zwiekszone wyplaty w kazdym obrocie.",
        "Blackjack na zywo w klimacie westernowym z opcjami zakladow bocznych. Profesjonalni krupierzy ze standardowymi zasadami blackjacka.",
        "Szybki baccarat z krotszymi oknami zakladow. Standardowe zasady baccarat z przyspieszonymi rundami.",
        "Nieograniczona liczba miejsc przy pokerowym stole z krupierem na zywo. Zaklady ante i call z opcjonalnym bonusowym zakladem bocznym.",
        "Program telewizyjny na zywo z obrotami kola grawitacyjnego. Segmenty mnoznikowe i rundy bonusowe dla wiekszych wygranych.",
        # These 3 are the original base-29 versions of GoO1000, 40MH, 100GC:
        "Boski slot z mnoznikami Zeusa i tematyka Olimpu. Kaskadowe bebny z mnoznikami do 1 000x i darmowymi spinami bonusowymi.",
        "Klasyczny owocowy automat z mechanika ognia. 40 linii wyplat z dzikimi symbolami, ognistymi re-spinami i rozszerzajacymi sie symbolami.",
        "Wedkarski automat z kolekcja zlotych monet. Zarzuc wedke po bonusowe zdobycze z re-spinami hold and win.",
    ],
    "de": [
        "Bonusrunden mit expandierenden Wilds und Multiplikator-Respins. Maximalgewinn bis zu 5.000x Ihrem Einsatz.",
        "Cluster-Auszahlungen mit kaskadierenden Symbolen und Freispielen. Multiplikatoren steigen mit jeder Kaskade.",
        "Die Bombenfunktion entfernt niedrigwertige Symbole und lost Kettenreaktionen aus. Hochvolatile Auszahlungen.",
        "Sammeln Sie Angler-Symbole fur sofortige Bargeldpreise. Fussball-Bonus mit Hold-and-Spin-Mechanik.",
        "Wahlen Sie Ihre Bonusrunde: Freispiele oder Geldrad. Drachen-Wilds multiplizieren Gewinne wahrend der Funktionen.",
        "Klebrige Wilds mit gestapelten Multiplikatoren wahrend der Freispiele. Wild-Regen-Funktion fur grossere Kombinationen.",
        "Plinko-Fallmechanik mit drei Topf-Ebenen. Landen Sie in den Goldtopfen fur die hochsten Multiplikatoren.",
        "Geister-Wilds verfolgen die Walzen uber mehrere Runden. Respins werden bei jedem gelandeten Geistersymbol ausgelost.",
        "Bis zu 117.649 Gewinnmoglichkeiten mit der Megaways-Engine. Drachen-Topf-Jackpots in jeder Runde verfugbar.",
        "Irisch thematisierter Bonus mit Gluckstein-Multiplikatoren. Freispiele mit progressiver Multiplikatorleiter.",
        "Der Mysterienladen vergibt zufallige Bonuspreise. Wahlen Sie Gegenstande fur Sofortgewinne oder Freispiel-Zugang.",
        "Agyptisches Abenteuer mit Code-Knack-Bonusmechanik. Schalten Sie Tresor-Symbole fur multiplizierte Auszahlungen frei.",
        "Die verfluchte Truhensammlung lost einen dreistufigen Bonus aus. Jede Truhenstufe erhoht die potenziellen Multiplikatoren.",
        "Hochvolatiler Wusten-Slot mit dauerhaften Multiplikatoren. Asche verwandelt sich beim Respin in Wilds.",
        "Dunkles Dynastiethema mit Todessymbol-Stapelung. Bonuskauf fur direkten Zugang zu den Funktionen verfugbar.",
        "Graben Sie sich durch Schichten fur versteckte Multiplikatoren und Preise. Jede Tiefenstufe erhoht das Belohnungspotenzial.",
        "Rote Lausbub-Wild-Symbole verbreiten sich wahrend der Freispiele uber die Walzen. Expandierende Wild-Walze bei Bonusauslosung.",
        "Extreme Volatilitat mit xWays- und xBet-Mechaniken. Mehrere Freispiel-Stufen mit steigenden Multiplikatoren.",
        "Blitzways-Mechanik mit schnellen Symboltransformationen. Dead-or-Alive-Bonus mit klebrigen Wilds.",
        "Machttore offnen progressive Freispiel-Stufen. Multiplikator-Symbole sammeln sich uber Bonusrunden.",
        "Mysterie-Symbole enthullen passende Icons fur grossere Gewinne. Koniglicher Bonus mit multiplizierten Gewinnlinien.",
        "Live-Roulette mit Schwerkraft-Multiplikator-Tropfen. Zufallige Zahlen erhalten erhohte Auszahlungen pro Runde.",
        "Live-Blackjack im Western-Thema mit Nebenwett-Optionen. Professionelle Dealer mit Standard-Blackjack-Regeln.",
        "Schnelles Baccarat mit kurzeren Wettfenstern. Standard-Baccarat-Regeln mit beschleunigten Runden.",
        "Unbegrenzte Platze am Poker-Tisch mit Live-Dealer. Ante- und Call-Einsatze mit optionaler Bonus-Nebenwette.",
        "Live-Gameshow mit Schwerkraft-Raddrehungen. Multiplikator-Segmente und Bonusrunden fur grossere Gewinne.",
        "Gottlicher Slot mit Zeus-Multiplikatoren und Olymp-Thema. Kaskadierende Walzen mit Multiplikatoren bis zu 1.000x und Bonus-Freispielen.",
        "Klassischer Frucht-Slot mit Feuer-Mechanik. 40 Gewinnlinien mit gestapelten Wilds, Feuer-Respins und expandierenden Symbolen.",
        "Angel-Abenteuer-Slot mit Goldmunzensammlung. Werfen Sie Ihre Angel fur Bonusfange mit Hold-and-Win-Respins aus.",
    ],
    "es": [
        "Rondas de bonificacion con comodines expansivos y re-giros con multiplicadores. Ganancia maxima hasta 5.000x tu apuesta.",
        "Pagos por cluster con simbolos en cascada y giros gratis. Los multiplicadores aumentan con cada cascada.",
        "La funcion bomba elimina simbolos de bajo valor y desencadena reacciones en cadena. Pagos de alta volatilidad.",
        "Recoge simbolos de pescador para premios en efectivo instantaneos. Bonus futbolistico con mecanica Hold and Spin.",
        "Elige tu ronda de bonificacion: giros gratis o rueda de efectivo. Los comodines dragon multiplican ganancias durante las funciones.",
        "Comodines pegajosos con multiplicadores apilados durante giros gratis. Funcion lluvia de comodines para mayores combinaciones.",
        "Mecanica de caida estilo Plinko con tres niveles de botes. Aterriza en los botes de oro para los multiplicadores mas altos.",
        "Los comodines fantasma acechan los rodillos durante varias rondas. Re-giros activados con cada simbolo fantasma aterrizado.",
        "Hasta 117.649 formas de ganar con el motor Megaways. Jackpots de botes dragon disponibles en cada giro.",
        "Bonus tematico irlandes con multiplicadores de piedra de la suerte. Giros gratis con escalera de multiplicadores progresivos.",
        "La tienda misteriosa otorga premios de bonificacion aleatorios. Elige objetos para ganancias instantaneas o entrada a giros gratis.",
        "Aventura egipcia con mecanica de bonus de descifrado. Desbloquea simbolos de caja fuerte para pagos multiplicados.",
        "La coleccion de cofres malditos activa un bonus de tres niveles. Cada nivel de cofre aumenta los multiplicadores potenciales.",
        "Tragamonedas de alta volatilidad con tema desertico y multiplicadores persistentes. Las cenizas se transforman en comodines durante el re-giro.",
        "Tema de dinastia oscura con apilamiento de simbolos de muerte. Compra de bonus disponible para acceso directo a las funciones.",
        "Excava a traves de capas para multiplicadores y premios ocultos. Cada nivel de profundidad aumenta el potencial de recompensa.",
        "Los simbolos comodin del pillo rojo se extienden por los rodillos durante los giros gratis. Rodillo comodin expansivo al activar el bonus.",
        "Volatilidad extrema con mecanicas xWays y xBet. Multiples niveles de giros gratis con multiplicadores crecientes.",
        "Mecanica Blitzways con transformaciones rapidas de simbolos. Bonus estilo Dead or Alive con comodines pegajosos.",
        "Las puertas del poder abren niveles progresivos de giros gratis. Los simbolos multiplicadores se acumulan durante las rondas de bonus.",
        "Los simbolos misteriosos revelan iconos coincidentes para mayores ganancias. Bonus real con lineas de pago multiplicadas.",
        "Ruleta en vivo con caidas de multiplicador por gravedad. Numeros aleatorios reciben pagos aumentados en cada ronda.",
        "Blackjack en vivo con tema del oeste y opciones de apuestas laterales. Crupieres profesionales con reglas estandar de blackjack.",
        "Baccarat rapido con ventanas de apuestas mas cortas. Reglas estandar de baccarat con rondas aceleradas.",
        "Asientos ilimitados en la mesa de poker con crupier en vivo. Apuestas ante y call con apuesta lateral de bonificacion opcional.",
        "Programa de juegos en vivo con giros de rueda gravitacional. Segmentos multiplicadores y rondas de bonus para mayores ganancias.",
        "Tragamonedas divino con multiplicadores de Zeus y tema del Olimpo. Rodillos en cascada con multiplicadores hasta 1.000x y giros gratis de bonificacion.",
        "Tragamonedas clasico de frutas con mecanicas de fuego. 40 lineas de pago con comodines apilados, re-giros de fuego y simbolos expansivos.",
        "Tragamonedas de aventura de pesca con coleccion de monedas de oro. Lanza tu linea para capturas de bonificacion con re-giros hold and win.",
    ],
    "en": [
        "Bonus rounds with expanding wilds and multiplier re-spins. Max win up to 5,000x your stake.",
        "Cluster pays with cascading symbols and free spins. Multipliers increase with each cascade.",
        "Bomb feature removes low-value symbols and triggers chain reactions. High volatility payouts.",
        "Collect fisherman symbols for instant cash prizes. Football-themed bonus with Hold and Spin mechanic.",
        "Choose your bonus round: free spins or cash wheel. Dragon wilds multiply wins during features.",
        "Sticky wilds with stacked multipliers during free spins. Wild rain feature for bigger combinations.",
        "Plinko-style drop mechanic with three pot levels. Land in gold pots for the highest multipliers.",
        "Ghost wilds haunt the reels for multiple rounds. Respins triggered with each landed ghost symbol.",
        "Up to 117,649 ways to win with the Megaways engine. Dragon pot jackpots available every spin.",
        "Irish-themed bonus with lucky stone multipliers. Free spins with progressive multiplier ladder.",
        "Mystery shop awards random bonus prizes. Pick items for instant wins or free spins entry.",
        "Egyptian adventure with code-cracking bonus mechanic. Unlock vault symbols for multiplied payouts.",
        "Cursed chest collection triggers a three-tier bonus. Each chest tier increases potential multipliers.",
        "High volatility desert-themed slot with persistent multipliers. Ashes transform into wilds during respin.",
        "Dark dynasty theme with death symbol stacking. Bonus buy available for direct feature access.",
        "Dig through layers for hidden multipliers and prizes. Each depth level increases reward potential.",
        "Red rascal wild symbols spread across the reels during free spins. Expanding wild reel on bonus trigger.",
        "Extreme volatility with xWays and xBet mechanics. Multiple free spin levels with increasing multipliers.",
        "Blitzways mechanic with rapid symbol transformations. Dead or Alive themed bonus with sticky wilds.",
        "Power gates open progressive free spin levels. Multiplier symbols collect across bonus rounds.",
        "Mystery symbols reveal matching icons for bigger wins. Royal bonus with multiplied paylines.",
        "Live roulette with gravity multiplier drops. Random numbers receive boosted payouts each round.",
        "Live blackjack in western theme with side bet options. Professional dealers with standard blackjack rules.",
        "Fast-paced baccarat with shorter betting windows. Standard baccarat rules with accelerated rounds.",
        "Unlimited seats at the poker table with live dealer. Ante and call bets with optional bonus side bet.",
        "Live game show with gravity wheel spins. Multiplier segments and bonus rounds for bigger wins.",
        "Divine slot with Zeus multipliers and Olympus theme. Cascading reels with multipliers up to 1,000x and bonus free spins.",
        "Classic fruit slot with fire mechanics. 40 paylines with stacked wilds, fire respins and expanding symbols.",
        "Fishing adventure slot with golden coin collection. Cast your line for bonus catches with hold and win respins.",
    ],
    "pt": [
        "Rodadas de bonus com wilds expansivos e re-spins com multiplicadores. Ganho maximo ate 5.000x sua aposta.",
        "Pagamentos por cluster com simbolos em cascata e rodadas gratis. Multiplicadores aumentam a cada cascata.",
        "A funcao bomba remove simbolos de baixo valor e aciona reacoes em cadeia. Pagamentos de alta volatilidade.",
        "Colete simbolos de pescador para premios em dinheiro instantaneos. Bonus com tema de futebol e mecanica Hold and Spin.",
        "Escolha sua rodada de bonus: rodadas gratis ou roda de dinheiro. Wilds dragao multiplicam ganhos durante as funcoes.",
        "Wilds fixos com multiplicadores empilhados durante rodadas gratis. Funcao chuva de wilds para combinacoes maiores.",
        "Mecanica de queda estilo Plinko com tres niveis de potes. Aterrisse nos potes de ouro para os maiores multiplicadores.",
        "Wilds fantasma assombram os rolos por varias rodadas. Re-spins acionados com cada simbolo fantasma.",
        "Ate 117.649 formas de ganhar com o motor Megaways. Jackpots de potes dragao disponiveis a cada giro.",
        "Bonus com tema irlandes e multiplicadores de pedra da sorte. Rodadas gratis com escada de multiplicadores progressivos.",
        "A loja misteriosa concede premios de bonus aleatorios. Escolha itens para ganhos instantaneos ou entrada em rodadas gratis.",
        "Aventura egipcia com mecanica de bonus de decodificacao. Desbloqueie simbolos de cofre para pagamentos multiplicados.",
        "A colecao de baus amaldicoados aciona um bonus de tres niveis. Cada nivel de bau aumenta os multiplicadores potenciais.",
        "Slot de alta volatilidade com tema desertico e multiplicadores persistentes. Cinzas se transformam em wilds durante re-spin.",
        "Tema de dinastia sombria com empilhamento de simbolos de morte. Compra de bonus disponivel para acesso direto as funcoes.",
        "Cave atraves das camadas para multiplicadores e premios escondidos. Cada nivel de profundidade aumenta o potencial de recompensa.",
        "Simbolos wild do trapaceiro vermelho se espalham pelos rolos durante rodadas gratis. Rolo wild expansivo ao acionar o bonus.",
        "Volatilidade extrema com mecanicas xWays e xBet. Multiplos niveis de rodadas gratis com multiplicadores crescentes.",
        "Mecanica Blitzways com transformacoes rapidas de simbolos. Bonus estilo Dead or Alive com wilds fixos.",
        "Portoes de poder abrem niveis progressivos de rodadas gratis. Simbolos multiplicadores se acumulam durante rodadas de bonus.",
        "Simbolos misteriosos revelam icones correspondentes para maiores ganhos. Bonus real com linhas de pagamento multiplicadas.",
        "Roleta ao vivo com quedas de multiplicador por gravidade. Numeros aleatorios recebem pagamentos aumentados a cada rodada.",
        "Blackjack ao vivo com tema western e opcoes de apostas laterais. Dealers profissionais com regras padrao de blackjack.",
        "Baccarat rapido com janelas de apostas mais curtas. Regras padrao de baccarat com rodadas aceleradas.",
        "Lugares ilimitados na mesa de poker com dealer ao vivo. Apostas ante e call com aposta lateral de bonus opcional.",
        "Game show ao vivo com giros da roda gravitacional. Segmentos multiplicadores e rodadas de bonus para maiores ganhos.",
        "Slot divino com multiplicadores de Zeus e tema do Olimpo. Rolos em cascata com multiplicadores ate 1.000x e rodadas gratis de bonus.",
        "Slot classico de frutas com mecanicas de fogo. 40 linhas de pagamento com wilds empilhados, re-spins de fogo e simbolos expansivos.",
        "Slot de aventura de pesca com colecao de moedas de ouro. Lance sua linha para capturas de bonus com re-spins hold and win.",
    ],
}

# ── Metidia link section translations ──
METIDIA_SECTIONS = {
    "fr": {
        "evo_title": "Evolution Gaming - Casino en Direct",
        "evo_descs": [
            "Guide complet d'Evolution Gaming sur la plateforme Roobet.",
            "Decouvrez les game shows en direct d'Evolution Gaming sur Roobet.",
            "Jouez a la Roulette en Direct Evolution sur Roobet.",
            "XXXtreme Lightning Roulette d'Evolution sur Roobet.",
            "Lightning Baccarat d'Evolution Gaming sur Roobet.",
            "Monopoly Live d'Evolution Gaming sur Roobet.",
            "Championnat de Casino en Direct sur Roobet.",
            "Crazy Time Brasil d'Evolution Gaming sur Roobet.",
        ],
        "hack_title": "Hacksaw Gaming - Machines a Sous",
        "hack_descs": [
            "Machines a sous haute volatilite de Hacksaw Gaming sur Roobet.",
            "Serie de machines a sous Hacksaw Gaming sur Roobet.",
            "Machines a sous Hacksaw Gaming optimisees pour mobile sur Roobet.",
            "Fonction achat bonus dans les machines a sous Hacksaw Gaming sur Roobet.",
        ],
        "nolimit_title": "Nolimit City - Machines a Sous",
        "nolimit_descs": [
            "Machines a sous a volatilite extreme de Nolimit City sur Roobet.",
            "Machines a sous achat bonus de Nolimit City sur Roobet.",
            "Nouvelles machines a sous Nolimit City pour 2026 sur Roobet.",
            "Comparaison de Nolimit City, Hacksaw et Pragmatic sur Roobet.",
            "Meilleures machines a sous RTP de Nolimit City sur Roobet.",
        ],
    },
    "pl": {
        "evo_title": "Evolution Gaming - Kasyno na Zywo",
        "evo_descs": [
            "Kompletny przewodnik po Evolution Gaming na platformie Roobet.",
            "Odkryj programy telewizyjne na zywo Evolution Gaming na Roobet.",
            "Graj w Ruletke na Zywo Evolution na Roobet.",
            "XXXtreme Lightning Roulette od Evolution na Roobet.",
            "Lightning Baccarat od Evolution Gaming na Roobet.",
            "Monopoly Live od Evolution Gaming na Roobet.",
            "Mistrzostwa Kasyna na Zywo na Roobet.",
            "Crazy Time Brasil od Evolution Gaming na Roobet.",
        ],
        "hack_title": "Hacksaw Gaming - Automaty",
        "hack_descs": [
            "Automaty o wysokiej zmiennosci od Hacksaw Gaming na Roobet.",
            "Seria automatow Hacksaw Gaming na Roobet.",
            "Automaty Hacksaw Gaming zoptymalizowane na mobile na Roobet.",
            "Funkcja zakupu bonusu w automatach Hacksaw Gaming na Roobet.",
        ],
        "nolimit_title": "Nolimit City - Automaty",
        "nolimit_descs": [
            "Automaty o ekstremalnej zmiennosci od Nolimit City na Roobet.",
            "Automaty z zakupem bonusu od Nolimit City na Roobet.",
            "Nowosci automatow Nolimit City na 2026 na Roobet.",
            "Porownanie Nolimit City, Hacksaw i Pragmatic na Roobet.",
            "Najlepsze automaty RTP od Nolimit City na Roobet.",
        ],
    },
    "de": {
        "evo_title": "Evolution Gaming - Live Casino",
        "evo_descs": [
            "Umfassender Leitfaden zu Evolution Gaming auf der Roobet-Plattform.",
            "Entdecken Sie die Live-Gameshows von Evolution Gaming auf Roobet.",
            "Spielen Sie Live-Roulette von Evolution auf Roobet.",
            "XXXtreme Lightning Roulette von Evolution auf Roobet.",
            "Lightning Baccarat von Evolution Gaming auf Roobet.",
            "Monopoly Live von Evolution Gaming auf Roobet.",
            "Live Casino Meisterschaft auf Roobet.",
            "Crazy Time Brasil von Evolution Gaming auf Roobet.",
        ],
        "hack_title": "Hacksaw Gaming - Spielautomaten",
        "hack_descs": [
            "Hochvolatile Spielautomaten von Hacksaw Gaming auf Roobet.",
            "Hacksaw Gaming Spielautomaten-Serie auf Roobet.",
            "Hacksaw Gaming Spielautomaten fur Mobilgerate auf Roobet.",
            "Bonuskauf-Funktion in Hacksaw Gaming Spielautomaten auf Roobet.",
        ],
        "nolimit_title": "Nolimit City - Spielautomaten",
        "nolimit_descs": [
            "Extrem volatile Spielautomaten von Nolimit City auf Roobet.",
            "Bonuskauf-Spielautomaten von Nolimit City auf Roobet.",
            "Neue Nolimit City Spielautomaten 2026 auf Roobet.",
            "Vergleich von Nolimit City, Hacksaw und Pragmatic auf Roobet.",
            "Beste RTP Spielautomaten von Nolimit City auf Roobet.",
        ],
    },
    "es": {
        "evo_title": "Evolution Gaming - Casino en Vivo",
        "evo_descs": [
            "Guia completa de Evolution Gaming en la plataforma Roobet.",
            "Descubre los programas de juegos en vivo de Evolution Gaming en Roobet.",
            "Juega a la Ruleta en Vivo de Evolution en Roobet.",
            "XXXtreme Lightning Roulette de Evolution en Roobet.",
            "Lightning Baccarat de Evolution Gaming en Roobet.",
            "Monopoly Live de Evolution Gaming en Roobet.",
            "Campeonato de Casino en Vivo en Roobet.",
            "Crazy Time Brasil de Evolution Gaming en Roobet.",
        ],
        "hack_title": "Hacksaw Gaming - Tragamonedas",
        "hack_descs": [
            "Tragamonedas de alta volatilidad de Hacksaw Gaming en Roobet.",
            "Serie de tragamonedas Hacksaw Gaming en Roobet.",
            "Tragamonedas Hacksaw Gaming optimizados para movil en Roobet.",
            "Funcion de compra de bonus en tragamonedas Hacksaw Gaming en Roobet.",
        ],
        "nolimit_title": "Nolimit City - Tragamonedas",
        "nolimit_descs": [
            "Tragamonedas de volatilidad extrema de Nolimit City en Roobet.",
            "Tragamonedas de compra de bonus de Nolimit City en Roobet.",
            "Nuevos tragamonedas Nolimit City 2026 en Roobet.",
            "Comparacion de Nolimit City, Hacksaw y Pragmatic en Roobet.",
            "Mejores tragamonedas RTP de Nolimit City en Roobet.",
        ],
    },
    "en": {
        "evo_title": "Evolution Gaming - Live Casino",
        "evo_descs": [
            "Complete guide to Evolution Gaming on the Roobet platform.",
            "Discover Evolution Gaming live game shows on Roobet.",
            "Play Evolution Live Roulette on Roobet.",
            "XXXtreme Lightning Roulette by Evolution on Roobet.",
            "Lightning Baccarat by Evolution Gaming on Roobet.",
            "Monopoly Live by Evolution Gaming on Roobet.",
            "Live Casino Championship on Roobet.",
            "Crazy Time Brasil by Evolution Gaming on Roobet.",
        ],
        "hack_title": "Hacksaw Gaming - Slots",
        "hack_descs": [
            "High volatility slots by Hacksaw Gaming on Roobet.",
            "Hacksaw Gaming slots series on Roobet.",
            "Hacksaw Gaming mobile-optimized slots on Roobet.",
            "Bonus buy feature in Hacksaw Gaming slots on Roobet.",
        ],
        "nolimit_title": "Nolimit City - Slots",
        "nolimit_descs": [
            "Extreme volatility slots by Nolimit City on Roobet.",
            "Bonus buy slots by Nolimit City on Roobet.",
            "New Nolimit City slots 2026 on Roobet.",
            "Nolimit City vs Hacksaw vs Pragmatic comparison on Roobet.",
            "Best RTP slots by Nolimit City on Roobet.",
        ],
    },
    "pt": {
        "evo_title": "Evolution Gaming - Casino ao Vivo",
        "evo_descs": [
            "Guia completo do Evolution Gaming na plataforma Roobet.",
            "Descubra os game shows ao vivo do Evolution Gaming no Roobet.",
            "Jogue Roleta ao Vivo Evolution no Roobet.",
            "XXXtreme Lightning Roulette da Evolution no Roobet.",
            "Lightning Baccarat da Evolution Gaming no Roobet.",
            "Monopoly Live da Evolution Gaming no Roobet.",
            "Campeonato de Casino ao Vivo no Roobet.",
            "Crazy Time Brasil da Evolution Gaming no Roobet.",
        ],
        "hack_title": "Hacksaw Gaming - Slots",
        "hack_descs": [
            "Slots de alta volatilidade da Hacksaw Gaming no Roobet.",
            "Serie de slots Hacksaw Gaming no Roobet.",
            "Slots Hacksaw Gaming otimizados para mobile no Roobet.",
            "Funcao de compra de bonus nos slots Hacksaw Gaming no Roobet.",
        ],
        "nolimit_title": "Nolimit City - Slots",
        "nolimit_descs": [
            "Slots de volatilidade extrema da Nolimit City no Roobet.",
            "Slots de compra de bonus da Nolimit City no Roobet.",
            "Novos slots Nolimit City 2026 no Roobet.",
            "Comparacao de Nolimit City, Hacksaw e Pragmatic no Roobet.",
            "Melhores slots RTP da Nolimit City no Roobet.",
        ],
    },
}

# ── Metidia link URLs (same for all languages) ──
METIDIA_EVO_URLS = [
    ("https://metidia.com/evolution-gaming-roobet/", "Evolution Gaming Roobet"),
    ("https://metidia.com/evolution-gaming-live-game-shows-roobet/", "Evolution Gaming Live Game Shows"),
    ("https://metidia.com/evolution-live-roulette-roobet/", "Evolution Live Roulette"),
    ("https://metidia.com/xxxtreme-lightning-roulette-roobet/", "XXXtreme Lightning Roulette"),
    ("https://metidia.com/lightning-baccarat-evolution-roobet/", "Lightning Baccarat Evolution"),
    ("https://metidia.com/monopoly-live-evolution-roobet/", "Monopoly Live Evolution"),
    ("https://metidia.com/live-casino-championship-roobet/", "Live Casino Championship"),
    ("https://metidia.com/crazy-time-brasil-evolution-roobet/", "Crazy Time Brasil Evolution"),
]

METIDIA_HACK_URLS = [
    ("https://metidia.com/hacksaw-gaming-volatilite-roobet/", "Hacksaw Gaming Volatilite"),
    ("https://metidia.com/hacksaw-gaming-serie-le-roobet/", "Hacksaw Gaming Serie"),
    ("https://metidia.com/hacksaw-gaming-slots-mobile-roobet/", "Hacksaw Gaming Slots Mobile"),
    ("https://metidia.com/hacksaw-gaming-bonus-buy-roobet/", "Hacksaw Gaming Bonus Buy"),
]

METIDIA_NOLIMIT_URLS = [
    ("https://metidia.com/nolimit-city-volatilite-extreme-roobet/", "Nolimit City Volatilite Extreme"),
    ("https://metidia.com/nolimit-city-bonus-buy-roobet/", "Nolimit City Bonus Buy"),
    ("https://metidia.com/nolimit-city-nouveautes-2026-roobet/", "Nolimit City Nouveautes 2026"),
    ("https://metidia.com/nolimit-city-vs-hacksaw-vs-pragmatic-roobet/", "Nolimit City vs Hacksaw vs Pragmatic"),
    ("https://metidia.com/nolimit-city-rtp-slots-roobet/", "Nolimit City RTP Slots"),
]

# ── Base game names (29 games in order as they appear in the FR index) ──
BASE_GAME_NAMES = [
    "Joker's Revenge", "Candy Rush", "Skeleton Bombs", "Big Bass Football Bonanza",
    "Dragon's Gate Bonus Choice", "The Big Dog House", "Triple Pot Plinko Hercules",
    "Great Ghosts", "Dragon Pots Megaways", "The Blarney Stone",
    "Mr Null's Wicked Wares", "Code of Cairo", "3 Cursed Chests", "Sand and Ashes",
    "Dynasty of Death", "Le Digger", "Red Rascal", "Punk Rocker 3",
    "Fate of Dead Blitzways", "Gates of Power", "King's Mystery",
    "Gravity Roulette", "Gold Saloon Blackjack", "Speed Baccarat",
    "Infinite Casino Hold'em", "Gravity Wheel",
    "Gates of Olympus 1000", "40 Mega Hotfire", "100 Golden Coins: Reel Fishing",
]

BASE_GAME_PROVIDERS = [
    "Pragmatic Play", "Pragmatic Play", "Pragmatic Play", "Pragmatic Play",
    "Pragmatic Play", "Pragmatic Play", "Pragmatic Play",
    "Pragmatic Play", "Pragmatic Play", "Pragmatic Play",
    "Pragmatic Play", "Fat Panda and Pragmatic Play", "Hacksaw Gaming", "Hacksaw Gaming",
    "Hacksaw Gaming", "Hacksaw Gaming", "Hacksaw Gaming", "Nolimit City",
    "Play'n GO", "BGaming", "Playtech",
    "Pragmatic Play Live", "Pragmatic Play Live", "Live Casino Provider",
    "Live Casino Provider", "Pragmatic Play Live",
    "Pragmatic Play", "Fazi", "Pragmatic Play",
]

BASE_GAME_SLUGS = [
    "jokers-revenge", "candy-rush", "skeleton-bombs", "big-bass-football-bonanza",
    "dragons-gate-bonus-choice", "the-big-dog-house", "triple-pot-plinko-hercules",
    "great-ghosts", "dragon-pots-megaways", "the-blarney-stone",
    "mr-nulls-wicked-wares", "code-of-cairo", "3-cursed-chests", "sand-and-ashes",
    "dynasty-of-death", "le-digger", "red-rascal", "punk-rocker-3",
    "fate-of-dead-blitzways", "gates-of-power", "kings-mystery",
    "gravity-roulette", "gold-saloon-blackjack", "speed-baccarat",
    "infinite-casino-holdem", "gravity-wheel",
    "gates-of-olympus-1000", "40-mega-hotfire", "100-golden-coins-reel-fishing",
]

BASE_GAME_CATEGORIES = [
    "Slot","Slot","Slot","Slot","Slot","Slot","Slot","Slot","Slot","Slot",
    "Slot","Slot","Slot","Slot","Slot","Slot","Slot","Slot","Slot","Slot","Slot",
    "Live Casino","Live Casino","Live Casino","Live Casino","Live Game Show",
    "Slot","Slot","Slot",
]

BASE_GAME_CAT_CLASSES = [
    "","","","","","","","","","","","","","","","","","","","","",
    " live"," live"," live"," live"," live",
    "","","",
]

# French descriptions (from current index.html, in order):
BASE_FR_DESCS = [
    "Tours bonus avec wilds expansifs et re-spins multiplicateurs. Gain max jusqu'a 5 000x votre mise.",
    "Paiements par cluster avec symboles en cascade et tours gratuits. Les multiplicateurs augmentent a chaque cascade.",
    "La fonction bombe supprime les symboles de faible valeur et declenche des reactions en chaine. Paiements a haute volatilite.",
    "Collectez les symboles pecheur pour des prix cash instantanes. Bonus sur theme football avec mecanique Hold and Spin.",
    "Choisissez votre tour bonus : tours gratuits ou roue cash. Les wilds dragon multiplient les gains pendant les fonctions.",
    "Wilds collants avec multiplicateurs empiles pendant les tours gratuits. Fonction pluie de wilds pour de plus grandes combinaisons.",
    "Mecanique de chute style Plinko avec trois niveaux de pots. Atterrissez dans les pots d'or pour les multiplicateurs les plus eleves.",
    "Les wilds fantomes hantent les rouleaux sur plusieurs tours. Re-spins declenches avec chaque symbole fantome atterri.",
    "Jusqu'a 117 649 facons de gagner avec le moteur Megaways. Jackpots de pots dragon disponibles a chaque tour.",
    "Bonus sur theme irlandais avec multiplicateurs de pierre porte-bonheur. Tours gratuits avec echelle de multiplicateurs progressifs.",
    "La boutique mystere attribue des prix bonus aleatoires. Choisissez des objets pour des gains instantanes ou l'entree en tours gratuits.",
    "Aventure egyptienne avec mecanique bonus de dechiffrage. Debloquez les symboles de coffre-fort pour des paiements multiplies.",
    "La collection de coffres maudits declenche un bonus a trois niveaux. Chaque niveau de coffre augmente les multiplicateurs potentiels.",
    "Machine a sous haute volatilite sur theme desertique avec multiplicateurs persistants. Les cendres se transforment en wilds lors du respin.",
    "Theme de dynastie sombre avec empilage de symboles de mort. Achat bonus disponible pour un acces direct aux fonctions.",
    "Creusez a travers les couches pour des multiplicateurs et prix caches. Chaque niveau de profondeur augmente le potentiel de recompense.",
    "Les symboles wild coquin se repandent sur les rouleaux pendant les tours gratuits. Rouleau wild expansif lors du declenchement du bonus.",
    "Volatilite extreme avec mecaniques xWays et xBet. Plusieurs niveaux de tours gratuits avec multiplicateurs croissants.",
    "Mecanique Blitzways avec transformations rapides de symboles. Bonus sur theme Dead or Alive avec wilds collants.",
    "Les portes de puissance s'ouvrent pour des niveaux progressifs de tours gratuits. Les symboles multiplicateurs se collectent a travers les tours bonus.",
    "Les symboles mystere revelent des icones correspondantes pour de plus gros gains. Tour bonus royal avec lignes de paiement multipliees.",
    "Roulette en direct avec chutes de multiplicateurs par gravite. Des numeros aleatoires recoivent des paiements augmentes a chaque tour.",
    "Blackjack en direct sur theme western avec options de mises laterales. Croupiers professionnels avec regles standard du blackjack.",
    "Baccarat a rythme rapide avec fenetres de paris plus courtes. Regles standard du baccarat avec tours acceleres.",
    "Places illimitees a la table de poker avec croupier en direct. Mises ante et call avec mise laterale bonus optionnelle.",
    "Game show en direct avec tours de roue a gravite. Segments multiplicateurs et tours bonus pour des gains plus importants.",
    "Machine a sous divine avec multiplicateurs Zeus et theme Olympe. Rouleaux en cascade avec multiplicateurs jusqu'a 1 000x et tours gratuits bonus.",
    "Machine a sous classique aux fruits avec mecaniques de feu. 40 lignes de paiement avec des wilds empiles, des re-spins de feu et des symboles expansifs.",
    "Machine a sous aventure de peche avec collection de pieces d'or. Lancez votre ligne pour des prises bonus avec des re-spins hold and win.",
]

# ── Language switcher links (relative paths) ──
def make_lang_switcher(active_lang, is_root=False):
    """Build the lang switcher HTML.
    For root (FR): links are ./, pl/, de/, es/, en/, pt/
    For subpages: links are ../, ../pl/, ../de/, ../es/, ../en/, ../pt/
    """
    prefix = "" if is_root else "../"
    langs = [
        ("fr", "FR", f"{prefix}" if not is_root else "./"),
        ("pl", "PL", f"{prefix}pl/"),
        ("de", "DE", f"{prefix}de/"),
        ("es", "ES", f"{prefix}es/"),
        ("en", "EN", f"{prefix}en/"),
        ("pt", "PT", f"{prefix}pt/"),
    ]
    if is_root:
        langs[0] = ("fr", "FR", "./")
    else:
        langs[0] = ("fr", "FR", "../")
    
    parts = []
    for code, label, href in langs:
        cls = ' class="active"' if code == active_lang else ''
        parts.append(f'<a href="{href}"{cls}>{label}</a>')
    return '<div class="lang-switcher">' + ''.join(parts) + '</div>'

# ── hreflang block ──
HREFLANG_BLOCK = """    <link rel="alternate" hreflang="fr" href="https://betscorecasino.games/">
    <link rel="alternate" hreflang="en" href="https://vulkanbet.us.com/">
    <link rel="alternate" hreflang="pt" href="https://betscorecasino.games/pt/">
    <link rel="alternate" hreflang="es" href="https://betscorecasino.games/es/">
    <link rel="alternate" hreflang="de" href="https://betscorecasino.games/de/">
    <link rel="alternate" hreflang="pl" href="https://betscorecasino.games/pl/">
    <link rel="alternate" hreflang="x-default" href="https://vulkanbet.us.com/">"""

# ── Build a game card HTML ──
def game_card_html(img_prefix, slug, name, provider, category, cat_class, desc):
    img_file = slug + ".webp"
    # Fix special case for 100-golden-coins -> 100-golden-coins-reel-fishing.webp
    if slug == "100-golden-coins-reel-fishing":
        img_file = "100-golden-coins-reel-fishing.webp"
    cat_cls = f' class="game-card-category{cat_class}"' if cat_class else ' class="game-card-category"'
    return f"""                <div class="game-card">
                    <div class="game-card-img"><img src="{img_prefix}images/{img_file}" alt="{name}" width="400" height="300" loading="lazy"></div>
                    <div class="game-card-body">
                        <div class="game-card-name">{name}</div>
                        <div class="game-card-provider">{provider}</div>
                        <span{cat_cls}>{category}</span>
                        <div class="game-card-desc">{desc}</div>
                    </div>
                </div>"""

# ── Build a metidia link card ──
def link_card_html(url, title, desc):
    return f"""                <div class="link-card">
                    <a href="{url}">{title}</a>
                    <p>{desc}</p>
                </div>"""

# ── Build full page ──
def build_page(lang_key):
    cfg = CFG[lang_key]
    is_root = (cfg["output"] == "index.html")
    img_prefix = cfg["img_prefix"]  # "" for root, "../" for subpages
    
    # Get game descriptions for this language
    if lang_key == "fr":
        game_descs = BASE_FR_DESCS
    else:
        game_descs = BASE_GAME_DESCS[lang_key]
    
    # Build base 29 game cards
    game_cards = []
    for i in range(29):
        game_cards.append(game_card_html(
            img_prefix, BASE_GAME_SLUGS[i], BASE_GAME_NAMES[i],
            BASE_GAME_PROVIDERS[i], BASE_GAME_CATEGORIES[i],
            BASE_GAME_CAT_CLASSES[i], game_descs[i]
        ))
    
    # Add extra games for this language
    extra_slugs = cfg.get("extra_games", [])
    for eslug in extra_slugs:
        meta = EXTRA_GAME_META.get(eslug)
        if not meta:
            continue
        desc = EXTRA_DESCS.get(lang_key, {}).get(eslug, "")
        img_file = meta["img"]
        game_cards.append(game_card_html(
            img_prefix, img_file.replace(".webp",""), meta["name"],
            meta["provider"], meta["category"], meta["cat_class"], desc
        ))
    
    games_html = "\n\n".join(game_cards)
    
    # Build metidia sections
    met = METIDIA_SECTIONS[lang_key]
    
    evo_cards = "\n".join([link_card_html(u, t, d) for (u,t), d in zip(METIDIA_EVO_URLS, met["evo_descs"])])
    hack_cards = "\n".join([link_card_html(u, t, d) for (u,t), d in zip(METIDIA_HACK_URLS, met["hack_descs"])])
    nolimit_cards = "\n".join([link_card_html(u, t, d) for (u,t), d in zip(METIDIA_NOLIMIT_URLS, met["nolimit_descs"])])
    
    # Build FAQ HTML
    faq_html = ""
    for q, a in cfg["faqs"]:
        faq_html += f"""                <div class="faq-item">
                    <button class="faq-question">
                        {q}
                        <span class="faq-arrow">&#9660;</span>
                    </button>
                    <div class="faq-answer">{a}</div>
                </div>
"""
    
    # Build steps HTML
    steps_html = ""
    for step in cfg["steps"]:
        steps_html += f"""                <div class="step-item">
                    <div class="step-number">{step[0]}</div>
                    <div class="step-title">{step[1]}</div>
                    <div class="step-text">{step[2]}</div>
                </div>
"""
    
    # Build info blocks HTML
    # We reuse the same SVG icons from the base template
    info_svgs = [
        '<svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg"><rect x="4" y="6" width="24" height="20" rx="3" stroke="#7aa2f7" stroke-width="2" fill="none"/><line x1="12" y1="6" x2="12" y2="26" stroke="#7aa2f7" stroke-width="1.5"/><line x1="20" y1="6" x2="20" y2="26" stroke="#7aa2f7" stroke-width="1.5"/><line x1="4" y1="14" x2="28" y2="14" stroke="#7aa2f7" stroke-width="1.5"/><line x1="4" y1="20" x2="28" y2="20" stroke="#7aa2f7" stroke-width="1.5"/><circle cx="8" cy="3" r="2" fill="#3b82f6"/><circle cx="16" cy="3" r="2" fill="#3b82f6"/><circle cx="24" cy="3" r="2" fill="#3b82f6"/></svg>',
        '<svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg"><ellipse cx="16" cy="20" rx="12" ry="6" stroke="#a78bfa" stroke-width="2" fill="none"/><path d="M16 4 L12 14 L20 14 Z" stroke="#a78bfa" stroke-width="1.5" fill="none"/><circle cx="16" cy="10" r="2" fill="#a78bfa"/><circle cx="8" cy="18" r="1.5" fill="#7aa2f7"/><circle cx="16" cy="21" r="1.5" fill="#ef4444"/><circle cx="24" cy="18" r="1.5" fill="#22c55e"/><circle cx="12" cy="23" r="1.5" fill="#f59e0b"/><circle cx="20" cy="23" r="1.5" fill="#7aa2f7"/></svg>',
        '<svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M4 28 L4 8 L28 8" stroke="#6b7b8f" stroke-width="1.5"/><path d="M6 24 Q10 24 12 18 Q14 12 18 14 Q22 16 24 6" stroke="#f59e0b" stroke-width="2.5" fill="none" stroke-linecap="round"/><circle cx="24" cy="6" r="3" fill="#ef4444" stroke="#ef4444" stroke-width="1"/><path d="M22 4 L24 6 L26 4" stroke="#fff" stroke-width="1.5" fill="none"/></svg>',
        '<svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg"><circle cx="16" cy="16" r="11" stroke="#22c55e" stroke-width="2" fill="none"/><path d="M16 5 Q20 10 16 16 Q12 22 16 27" stroke="#22c55e" stroke-width="1.5" fill="none"/><path d="M16 5 Q12 10 16 16 Q20 22 16 27" stroke="#22c55e" stroke-width="1.5" fill="none"/><line x1="5" y1="12" x2="27" y2="12" stroke="#22c55e" stroke-width="1.2"/><line x1="5" y1="20" x2="27" y2="20" stroke="#22c55e" stroke-width="1.2"/></svg>',
    ]
    
    info_html = ""
    for i, (title, text) in enumerate(zip(cfg["info_titles"], cfg["info_texts"])):
        info_html += f"""                <div class="info-block">
                    <div class="info-block-icon">{info_svgs[i]}</div>
                    <div class="info-block-title">{title}</div>
                    <div class="info-block-text">{text}</div>
                </div>
"""
    
    # Build stats
    stats = cfg["stats"]  # list of [value, label] pairs
    stats_html = ""
    for val, lbl in stats:
        stats_html += f"""                <div class="stat-item">
                    <div class="stat-value">{val}</div>
                    <div class="stat-label">{lbl}</div>
                </div>
"""
    
    # Lang switcher
    lang_sw = make_lang_switcher(lang_key, is_root)
    
    # Sitemap link - relative path
    sitemap_href = "sitemap.xml" if is_root else "../sitemap.xml"
    
    # Favicon / asset paths
    fav_ico = f"{img_prefix}favicon.ico"
    fav_32 = f"{img_prefix}images/favicon-32x32.png"
    fav_16 = f"{img_prefix}images/favicon-16x16.png"
    apple_icon = f"{img_prefix}images/apple-touch-icon.png"
    banner_img = f"{img_prefix}images/banner-cta.webp"
    
    # Logo SVG (same for all pages)
    logo_svg = '<svg width="160" height="36" viewBox="0 0 160 36" fill="none" xmlns="http://www.w3.org/2000/svg"><rect x="1" y="1" width="34" height="34" rx="8" fill="#1a1035" stroke="#3b82f6" stroke-width="1.5"/><text x="18" y="25" text-anchor="middle" font-family="\'Segoe UI\',sans-serif" font-weight="700" font-size="18" fill="#fff">BS</text><rect x="6" y="28" width="22" height="3" rx="1.5" fill="#3b82f6"/><text x="46" y="25" font-family="\'Segoe UI\',sans-serif" font-weight="700" font-size="22" fill="#fff">Bet</text><text x="84" y="25" font-family="\'Segoe UI\',sans-serif" font-weight="700" font-size="22" fill="#3b82f6">Score</text></svg>'
    
    # Provider badges SVG HTML (same for all)
    provider_badges = [
        ("Pragmatic Play", "PP", "#3b82f6"),
        ("Hacksaw Gaming", "HG", "#ef4444"),
        ("Nolimit City", "NL", "#f59e0b"),
        ("Play'n GO", "PG", "#a78bfa"),
        ("BGaming", "BG", "#22c55e"),
        ("Playtech", "PT", "#06b6d4"),
        ("NetEnt", "NE", "#10b981"),
        ("Red Tiger", "RT", "#ef4444"),
        ("Yggdrasil", "YG", "#8b5cf6"),
        ("Evolution", "EV", "#f97316"),
        ("Betsoft", "BT", "#eab308"),
        ("Stakelogic", "SL", "#ec4899"),
    ]
    providers_html = ""
    for pname, code, color in provider_badges:
        providers_html += f"""                <div class="provider-badge">
                    <div class="provider-badge-logo"><svg width="36" height="36" viewBox="0 0 36 36" fill="none" xmlns="http://www.w3.org/2000/svg"><rect width="36" height="36" rx="6" fill="#1a2230"/><text x="18" y="23" text-anchor="middle" font-family="'Segoe UI',sans-serif" font-weight="700" font-size="14" fill="{color}">{code}</text></svg></div>
                    <div class="provider-badge-name">{pname}</div>
                </div>
"""
    
    # Payment row SVGs (same for all)
    payment_svgs = [
        '<svg width="48" height="28" viewBox="0 0 48 28" fill="none" xmlns="http://www.w3.org/2000/svg"><text x="24" y="18" text-anchor="middle" font-family="\'Segoe UI\',sans-serif" font-weight="700" font-size="12" fill="#1a1f71">VISA</text><rect x="0" y="0" width="48" height="3" fill="#1a1f71"/><rect x="0" y="25" width="48" height="3" fill="#f7a600"/></svg>',
        '<svg width="48" height="28" viewBox="0 0 48 28" fill="none" xmlns="http://www.w3.org/2000/svg"><circle cx="19" cy="14" r="9" fill="#eb001b" opacity="0.9"/><circle cx="29" cy="14" r="9" fill="#f79e1b" opacity="0.9"/><path d="M24 7.5 A9 9 0 0 1 24 20.5 A9 9 0 0 1 24 7.5" fill="#ff5f00"/></svg>',
        '<svg width="48" height="28" viewBox="0 0 48 28" fill="none" xmlns="http://www.w3.org/2000/svg"><circle cx="24" cy="14" r="11" fill="#f7931a"/><text x="24" y="19" text-anchor="middle" font-family="\'Segoe UI\',sans-serif" font-weight="700" font-size="14" fill="#fff">B</text></svg>',
        '<svg width="48" height="28" viewBox="0 0 48 28" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M24 2 L16 14 L24 19 L32 14 Z" fill="#627eea"/><path d="M24 19 L16 14 L24 26 L32 14 Z" fill="#3c3c3d" opacity="0.6"/></svg>',
        '<svg width="48" height="28" viewBox="0 0 48 28" fill="none" xmlns="http://www.w3.org/2000/svg"><circle cx="24" cy="14" r="11" fill="#26a17b"/><text x="24" y="12" text-anchor="middle" font-family="\'Segoe UI\',sans-serif" font-weight="700" font-size="8" fill="#fff">USDT</text><rect x="17" y="14" width="14" height="2" rx="1" fill="#fff"/><rect x="23" y="14" width="2" height="8" rx="1" fill="#fff"/></svg>',
        '<svg width="48" height="28" viewBox="0 0 48 28" fill="none" xmlns="http://www.w3.org/2000/svg"><circle cx="24" cy="14" r="11" fill="#bfbbbb"/><text x="24" y="19" text-anchor="middle" font-family="\'Segoe UI\',sans-serif" font-weight="700" font-size="14" fill="#fff">L</text></svg>',
        '<svg width="48" height="28" viewBox="0 0 48 28" fill="none" xmlns="http://www.w3.org/2000/svg"><rect x="2" y="2" width="44" height="24" rx="4" fill="#862165"/><text x="24" y="18" text-anchor="middle" font-family="\'Segoe UI\',sans-serif" font-weight="700" font-size="10" fill="#fff">Skrill</text></svg>',
        '<svg width="48" height="28" viewBox="0 0 48 28" fill="none" xmlns="http://www.w3.org/2000/svg"><rect x="2" y="2" width="44" height="24" rx="4" fill="#6c9a27"/><text x="24" y="18" text-anchor="middle" font-family="\'Segoe UI\',sans-serif" font-weight="600" font-size="8" fill="#fff">Neteller</text></svg>',
        '<svg width="48" height="28" viewBox="0 0 48 28" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M24 3 L8 10 L40 10 Z" fill="#6b7b8f"/><rect x="8" y="10" width="32" height="2" fill="#7a8599"/><rect x="11" y="12" width="4" height="10" fill="#6b7b8f"/><rect x="19" y="12" width="4" height="10" fill="#6b7b8f"/><rect x="27" y="12" width="4" height="10" fill="#6b7b8f"/><rect x="35" y="12" width="4" height="10" fill="#6b7b8f"/><rect x="8" y="22" width="32" height="3" rx="1" fill="#7a8599"/></svg>',
    ]
    payment_html = "\n".join([f'                <div class="payment-item">{svg}</div>' for svg in payment_svgs])
    
    # Read CSS from the base template (extract between <style> and </style>)
    css_match = re.search(r'<style>(.*?)</style>', BASE_HTML, re.DOTALL)
    css_content = css_match.group(1) if css_match else ""
    
    # Build the full HTML
    html = f"""<!DOCTYPE html>
<html lang="{cfg['html_lang']}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{cfg['title']}</title>
    <meta name="description" content="{cfg['description']}">
    <meta name="robots" content="index, follow">
    <link rel="canonical" href="{cfg['canonical']}">
{HREFLANG_BLOCK}
    <link rel="sitemap" type="application/xml" href="{sitemap_href}">
    <link rel="icon" type="image/x-icon" href="{fav_ico}">
    <link rel="icon" type="image/png" sizes="32x32" href="{fav_32}">
    <link rel="icon" type="image/png" sizes="16x16" href="{fav_16}">
    <link rel="apple-touch-icon" sizes="180x180" href="{apple_icon}">
    <meta property="og:title" content="{cfg['title']}">
    <meta property="og:description" content="{cfg['description']}">
    <meta property="og:type" content="website">
    <meta property="og:url" content="{cfg['canonical']}">
    <meta property="og:image" content="https://betscorecasino.games/images/banner-cta.webp">
    <style>{css_content}</style>
</head>
<body>

    <!-- HEADER -->
    <header class="site-header">
        <div class="logo">{logo_svg}</div>
        <p class="tagline">{cfg['tagline']}</p>
        {lang_sw}
    </header>

    <div class="container">

        <!-- ===== FEATURED GAMES GRID ===== -->
        <section class="featured-games">
            <h2 class="section-title">{cfg['featured_title']}</h2>
            <div class="games-grid">

{games_html}

            </div>
        </section>

        <!-- ===== H1 + TEXT BLOCK ===== -->
        <section class="text-section">
            <h1>{cfg['h1']}</h1>

            <p>{cfg['h1_p1']}</p>

            <p>{cfg['h1_p2']}</p>

            <p>{cfg['h1_p3']}</p>

            <p>{cfg['h1_p4']}</p>

            <div class="cta-group">
                <a href="#" class="cta-btn cta-primary">{cfg['cta1']}</a>
                <a href="#" class="cta-btn cta-secondary">{cfg['cta2']}</a>
                <a href="#" class="cta-btn cta-secondary">{cfg['cta3']}</a>
            </div>
        </section>

        <!-- ===== H2 + TEXT BLOCK ===== -->
        <section class="text-section">
            <h2>{cfg['h2']}</h2>

            <p>{cfg['h2_p1']}</p>

            <p>{cfg['h2_p2']}</p>

            <p>{cfg['h2_p3']}</p>

            <p>{cfg['h2_p4']}</p>

            <div class="cta-group">
                <a href="#" class="cta-btn cta-primary">{cfg['h2_cta1']}</a>
                <a href="#" class="cta-btn cta-secondary">{cfg['h2_cta2']}</a>
                <a href="#" class="cta-btn cta-secondary">{cfg['h2_cta3']}</a>
                <a href="#" class="cta-btn cta-secondary">{cfg['h2_cta4']}</a>
                <a href="#" class="cta-btn cta-secondary">{cfg['h2_cta5']}</a>
                <a href="#" class="cta-btn cta-secondary">{cfg['h2_cta6']}</a>
                <a href="#" class="cta-btn cta-secondary">{cfg['h2_cta7']}</a>
            </div>
        </section>

        <!-- ===== UX ELEMENTS ===== -->
        <section class="ux-section">
            <h2 class="section-title">{cfg['why_title']}</h2>

            <!-- Stats Bar -->
            <div class="stats-bar">
{stats_html}
            </div>

            <!-- Info Blocks -->
            <div class="info-blocks">
{info_html}
            </div>

            <!-- How to Get Started - Steps -->
            <h2 class="section-title">{cfg['steps_title']}</h2>
            <div class="steps-row">
{steps_html}
            </div>

            <!-- Game Providers -->
            <h2 class="section-title">{cfg['providers_title']}</h2>
            <div class="providers-row">
{providers_html}
            </div>

            <!-- Banner CTA -->
            <div class="banner-cta">
                <div class="banner-cta-img"><img src="{banner_img}" alt="BetScore Casino Games Slots Live Tables" width="640" height="180" loading="lazy"></div>
                <div class="banner-cta-title">{cfg['banner_title']}</div>
                <div class="banner-cta-text">{cfg['banner_text']}</div>
                <div class="cta-group" style="justify-content: center;">
                    <a href="#" class="cta-btn cta-primary">{cfg['banner_cta1']}</a>
                    <a href="#" class="cta-btn cta-secondary">{cfg['banner_cta2']}</a>
                </div>
            </div>

            <!-- Payment Methods -->
            <h2 class="section-title">{cfg['payment_title']}</h2>
            <div class="payment-row">
{payment_html}
            </div>

            <!-- FAQ Accordion -->
            <h2 class="section-title">{cfg['faq_title']}</h2>
            <div class="faq-list">
{faq_html}
            </div>
        </section>

        <!-- ===== EXISTING METIDIA LINK SECTIONS ===== -->
        <section class="links-section">
            <h2 class="section-title">{met['evo_title']}</h2>
            <div class="links-grid">
{evo_cards}
            </div>
        </section>

        <section class="links-section">
            <h2 class="section-title">{met['hack_title']}</h2>
            <div class="links-grid">
{hack_cards}
            </div>
        </section>

        <section class="links-section">
            <h2 class="section-title">{met['nolimit_title']}</h2>
            <div class="links-grid">
{nolimit_cards}
            </div>
        </section>

    </div>

    <!-- FOOTER -->
    <footer class="site-footer">
        <p>{cfg['footer']}</p>
        {lang_sw}
    </footer>

    <!-- FAQ Toggle Script -->
    <script>
        document.querySelectorAll('.faq-question').forEach(function(btn) {{
            btn.addEventListener('click', function() {{
                var item = this.parentElement;
                var isOpen = item.classList.contains('open');
                document.querySelectorAll('.faq-item').forEach(function(el) {{
                    el.classList.remove('open');
                }});
                if (!isOpen) {{
                    item.classList.add('open');
                }}
            }});
        }});
    </script>

</body>
</html>"""
    return html

# ── Generate all 6 pages ──
for lang in ["fr", "pl", "de", "es", "en", "pt"]:
    html = build_page(lang)
    output = CFG[lang]["output"]
    # Ensure directory exists
    out_dir = os.path.dirname(output)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    with open(output, "w") as f:
        f.write(html)
    total_games = 29 + len(CFG[lang].get("extra_games", []))
    print(f"  {lang}: {output} ({len(html):,} bytes, {total_games} games)")

print("\nAll 6 pages generated successfully!")

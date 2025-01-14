# Gamestyles sorted from easiest to hardest/most controversial
def get_questionset(style: str):
    global questionsets
    if style in questionsets.keys():
        return questionsets[style]
    else:
        return None
    
def get_styles():
    global questionsets
    return list(questionsets.keys())

controversial = [
    {"question": "Kuka todennäköisimmin juoksee Promenaden läpi pelkkä lakana päällään?"},
    {"question": "Kuka todennäköisimmin saa jättipotin laivan pelikoneesta?"},
    {"question": "Kuka todennäköisimmin menisi naimisiin rahasta?"},
    {"question": "Kumpi on paremman näköinen?"},
    {"question": "Kumman kanssa menisit mieluummin sänkyyn?"},
    {"question": "Kumpi on enemmän alfa?"},
    {"question": "Kumpi on enemmän simp?"},
    {"question": "Kuka todennäköisimmin unohtaa ystävänsä syntymäpäivän?"},
    {"question": "Kuka todennäköisimmin unohtaa avaimensa kotiin?"},
    {"question": "Kumpi on juonut enemmän?"},
    {"question": "Kumpi äänestää Trumpia?"},
    {"question": "Kumpi googlaa itseään (enemmän)?"},
    {"question": "Kuka todennäköisimmin myy sielunsa paholaiselle?"},
    {"question": "Kuka todennäköisimmin esiintyy alastonkuvissa?"},
    {"question": "Kuka todennäköisimmin varastaa ystävänsä kumppanin?"},
    {"question": "Kuka todennäköisimmin jää kiinni pettämisestä?"},
    {"question": "Kuka todennäköisimmin joutuu vankilaan?"},
    {"question": "Kuka todennäköisimmin valehtelee ikänsä?"},
    {"question": "Kuka todennäköisimmin käyttää huumeita?"},
    {"question": "Kuka todennäköisimmin osallistuu orgioihin?"},
    {"question": "Kuka todennäköisimmin tekee muovileikkauksia?"},
    {"question": "Kuka todennäköisimmin jättää laskut maksamatta?"},
    {"question": "Kuka todennäköisimmin ajaa humalassa?"},
    {"question": "Kuka todennäköisimmin menettää työnsä skandaalin takia?"},
    {"question": "Kuka todennäköisimmin valehtelee CV:ssä?"},
    {"question": "Kuka todennäköisimmin käyttää treffisovelluksia salaa?"},
    {"question": "Kuka todennäköisimmin osallistuu mielenosoituksiin?"},
    {"question": "Kuka todennäköisimmin jättää perheensä?"},
    {"question": "Kuka todennäköisimmin tekee rikosilmoituksen väärin perustein?"},
    {"question": "Kuka todennäköisimmin käyttää väärin yrityksen varoja?"},
    {"question": "Kuka todennäköisimmin osallistuu laittomiin vedonlyönteihin?"},
    {"question": "Kuka todennäköisimmin käyttää väärin lääkkeitä?"},
    {"question": "Kuka todennäköisimmin käyttää väärin sosiaalietuuksia?"},
    {"question": "Kuka todennäköisimmin osallistuu laittomiin maahanmuuttojärjestelyihin?"},
    {"question": "Kuka todennäköisimmin osallistuu laittomiin aseiden kauppoihin?"},
    {"question": "Kumman seksuaalisuus on enemmän kyseenalaista?"},
    {"question": "Kuka todennäköisimmin joutuu laivan putkaan?"},
    {"question": "Kumpi ottaa shotin?"},
    {"question": "Kumpi juo juomansa loppuun?"},
    {"question": "Kumpi puhuu englantia seuraavat 10 min?"},
    {"question": "Kumpi puhuu ruotsia seuraavat 10 min?"},
    {"question": "Kuka todennäköisemmin selviäisi nälkäpelistä ryhmän jäseniä vastaan?"},
    {"question": "Kuka todennäköisimmin tekee veropetoksen?"},
    {"question": "Kumpi voittaisi kaksintaistelun toista henkilöä vastaan?"},
    {"question": "Kuka todennäköisimmin rupeaa poliitikoksi?"},
    {"question": "Kumpi todennäköisimmin rupeaa nunnaksi/munkiksi?"},
    {"question": "Kuka todennäköisimmin rupeaa pornotähdeksi?"},
    {"question": "Kuka todennäköisimmin rupeaa alkoholistiksi?"},
    {"question": "Kuka todennäköisimmin rupeaa uskonnolliseksi johtajaksi?"},
    {"question": "Kummalla on paremmat tanssiliikkeet?"},
    {"question": "Kummalla on parempi keskiarvo?"},
    {"question": "Kumpi harrastaa enemmän seksiä?"},
    {"question": "Kuka todennäköisimmin ei kannata aborttia?"},
    {"question": "Kumpi on seksikkäämpi?"},
    {"question": "Kummalla on ollut enemmän seksikumppaneita?"},
    {"question": "Kuka todennäköisimmin etsii seksikumppaneita laivalta tänään?"},
    {"question": "Kumpi näyttää internetin selaushistoriansa?"},
    {"question": "Kuka todennäköisimmin flirttailee baaritiskillä saadakseen ilmaisen juoman?"},
    {"question": "Kumpi voisi mennä sokkotreffeille ilman tietoa parin sukupuolesta?"},
    {"question": "Kuka todennäköisimmin kokee, ettei yksi kumppani riitä?"},
    {"question": "Kuka todennäköisimmin eksyy matkalla lähikauppaan?"},
    {"question": "Kumpi voittaa beerpongissa?"},
    {"question": "Kuka todennäköisimmin unohtaa, missä hytti sijaitsee?"},
    {"question": "Kumpi todennäköisemmin menee aamulla laivan kylpylään?"},
    {"question": "Kuka todennäköisimmin järjestää epäviralliset bileet hyttikäytävällä?"},
    {"question": "Kuka todennäköisimmin pyytää ventovierasta laivalla feikkaamaan olevansa heidän puolisonsa?"},
    {"question": "Kuka todennäköisimmin yrittää vaihtaa hyttiä yöllä toisen matkustajan kanssa?"},
    {"question": "Kumpi unohtaa oman hyttinsä numeron?"},
    {"question": "Kuka todennäköisimmin onnistuu saamaan satunnaisen matkustajan hytin avaimen itselleen?"},
    {"question": "Kuka todennäköisimmin jää Tukholmaan?"},
    {"question": "Kuka todennäköisimmin elää kaksoiselämää?"}
]

questionsets = {
    'controversial': controversial
}
ᏚAMI YT X JISAN TCP BOT - MERGED
======================
Run:   pip install -r requirements.txt
       python main.py

Root folder      = updated bot (jisan_TCP_bot_updated) - ei ta ei run hobe.
Pb2/             = updated Pb2 + old Pb2 helper files (extra gulo merge kora hoise).
UPDATE (old file theke ana)
---------------------------
1) /5 + group (squad) packet: xC4.py er OpEnSq, cHSq, SEnd_InV, GenJoinSquadsPacket
   ekhon old file er version. Notun gulo *_new naam e rakha ache (OpEnSq_new ityadi).
   Old version Nu (3/4/5/6) thikmoto use kore, tai /3 /4 /6 o thik size e hobe.
2) MajorLogin: login_engine.py te USE_OLD_MAJORLOGIN (ekhon False kora ache, karon old payload server reject korse).
   Login fail korle False kore dao -> notun payload cholbe.

UPDATE 2
--------
- /5 command remove kora hoise (help menu theke o).
- Bot ke group e invite korle auto join hobe + ᏚAMI YT welcome message debe
  (WELCOME_TEXT, bot_core.py te; ek group e 30 min e ekbar).
- MahirAccepted -> JisanAccepted, "PLongDev" -> "ᏚAMI YT" nam bodle deya hoise.

UPDATE 3
--------
- /6 /3 /4 command remove kora hoise.
- Guild chat reply delay fix: SEndMsG er CLan branch ekhon old file er xSEndMsg use kore
  (fallback: NewClanChatPacket). Notun version xSEndMsg_new naam e ache.
- legacy_old_bot folder muche deya hoise (tomar original ᏚAMI YT_LAST_FILE.zip e backup ache).

UPDATE 4
--------
- Invite welcome fix: squad chat packet (xSEndMsgsQ) old file er version, ar welcome ekhon
  old file er moto squad owner uid e jay (age chat_code e jacchilo, tai msg dekha jacchilo na).
  Welcome delay 1 sec.

UPDATE 5
--------
- /help ar /jisan duto e same menu dekhay. Menu message gulor majhe gap 0.4s -> 0.1s (HELP_DELAY, bot_core.py).
- /lag (ar /stop lag) pura delete kora hoise.

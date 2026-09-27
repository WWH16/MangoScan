"""English / Filipino text for MangoScan.

English is the source language: every string in the templates and the code is
written in English and passed through `t()`. The FIL table below maps each
English string to its Filipino version. A string missing from the table simply
shows in English, so a new feature never breaks the Filipino page.

The Filipino text should be reviewed by a native speaker before release,
especially the treatment advice on the result page.
"""
from flask import Blueprint, g, redirect, request, url_for
from markupsafe import Markup

bp = Blueprint("i18n", __name__)

LANGS = ("en", "fil")
COOKIE = "lang"

FIL = {
    # ---------- Header and footer ----------
    "Skip to content": "Lumaktaw sa nilalaman",
    "MangoScan home": "Home ng MangoScan",
    "MangoScan, start a new scan": "MangoScan, magsimula ng bagong scan",
    "Mango disease checker": "Pantingin ng sakit ng mangga",
    "My scans": "Aking mga scan",
    "Log in": "Mag-log in",
    "Language": "Wika",
    "MangoScan · thesis prototype · HSV, GLCM and Hu features with an RBF SVM":
        "MangoScan · prototype para sa thesis · HSV, GLCM at Hu features gamit ang RBF SVM",

    # ---------- Landing page ----------
    "About MangoScan": "Tungkol sa MangoScan",
    "Check a mango for disease with one photo": "Suriin ang sakit ng mangga sa isang litrato",
    "Check a mango for disease with one photo.": "Suriin ang sakit ng mangga sa isang litrato.",
    "MangoScan tells you if the fruit is <strong>healthy</strong>, has <strong>anthracnose</strong> or has <strong>stem-end rot</strong>, and what to do with it.":
        "Sasabihin ng MangoScan kung ang bunga ay <strong>malusog</strong>, may <strong>anthracnose</strong>, o may <strong>stem-end rot</strong>, at kung ano ang gagawin dito.",
    "Free. No account needed.": "Libre. Hindi kailangan ng account.",
    "Example mangoes": "Mga halimbawang mangga",
    "A healthy green mango": "Isang malusog na berdeng mangga",
    "A mango with dark anthracnose patches": "Isang mangga na may maitim na mantsa ng anthracnose",
    "A ripe mango rotting from the stem end": "Isang hinog na manggang nabubulok mula sa tangkay",
    "Anthracnose": "Anthracnose",
    "Stem-end rot": "Stem-end rot",
    "How it works": "Paano ito gumagana",
    "Take a photo": "Kumuha ng litrato",
    "Fill the frame with one mango. Use a plain background and even light, with the stem end showing.":
        "Punuin ng isang mangga ang litrato. Gumamit ng payak na background at pantay na liwanag, at dapat kita ang tangkay.",
    "Example photo: one mango filling the frame":
        "Halimbawang litrato: isang manggang puno sa litrato",
    "MangoScan checks the peel": "Sinusuri ng MangoScan ang balat",
    "It looks at the colour, texture and shape of the skin. This takes a few seconds.":
        "Tinitingnan nito ang kulay, tekstura at hugis ng balat. Ilang segundo lang ito.",
    "If the photo is too dark, too blurry or has no mango in it, MangoScan asks for a new photo instead of guessing.":
        "Kung masyadong madilim, malabo, o walang mangga ang litrato, hihingi ang MangoScan ng bagong litrato sa halip na manghula.",
    "Find the mango in the photo": "Hanapin ang mangga sa litrato",
    "Look at the colour": "Tingnan ang kulay",
    "Look at the texture and shape": "Tingnan ang tekstura at hugis",
    "Pick the answer": "Piliin ang sagot",
    "Read the answer": "Basahin ang sagot",
    "You get the name of the disease, what to do with the fruit, and the bad spots marked on your photo.":
        "Makikita mo ang pangalan ng sakit, ang dapat gawin sa bunga, at ang mga sirang bahagi na may marka sa iyong litrato.",
    "The example mango with the diseased area boxed in red": "Ang halimbawang mangga na may pulang kahon sa bahaging may sakit",
    "Real result from MangoScan for the example mango.": "Tunay na resulta ng MangoScan para sa halimbawang mangga.",
    "The three answers": "Ang tatlong sagot",
    "Every scan ends with one of these, and what to do next.":
        "Bawat scan ay nagtatapos sa isa sa mga ito, kasama ang susunod na gagawin.",
    "Good to know": "Mabuting malaman",
    "No account needed": "Hindi kailangan ng account",
    "Anyone can scan. Nothing is kept unless you log in.":
        "Kahit sino ay puwedeng mag-scan. Walang itinatago maliban kung naka-log in ka.",
    "Save your scans": "I-save ang iyong mga scan",
    "With a free account, every scan and its photos are kept under My scans.":
        "Kapag may libreng account, nakatago ang bawat scan at ang mga litrato nito sa Aking mga scan.",
    "Open My scans": "Buksan ang Aking mga scan",
    "English or Filipino": "English o Filipino",
    "Choose your language in Settings.": "Piliin ang iyong wika sa Settings.",
    "Open Settings": "Buksan ang Settings",
    "Add it to your phone": "Ilagay sa iyong phone",
    "Install MangoScan on your home screen and open it like an app. Checking a photo still needs the internet.":
        "I-install ang MangoScan sa home screen at buksan ito na parang app. Kailangan pa rin ng internet para masuri ang litrato.",
    "How to install": "Paano i-install",
    "Have a mango with you?": "May mangga ka ba riyan?",
    "Take its photo now. It takes less than a minute.": "Kunan na ito ng litrato. Wala pang isang minuto ito.",

    # ---------- Scan screen ----------
    "Scan a mango": "I-scan ang mangga",
    "Scan a mango.": "I-scan ang mangga.",
    "Take one photo. MangoScan tells you if the fruit is <strong>healthy</strong>, has <strong>anthracnose</strong> or has <strong>stem-end rot</strong>, and what to do next.":
        "Kumuha ng isang litrato. Sasabihin ng MangoScan kung ang bunga ay <strong>malusog</strong>, may <strong>anthracnose</strong>, o may <strong>stem-end rot</strong>, at kung ano ang dapat gawin.",
    "Dismiss message": "Isara ang mensahe",
    "Fill the frame with the fruit. Plain background, even light, stem end showing.":
        "Punuin ng bunga ang litrato. Payak na background, pantay na liwanag, at kita ang tangkay.",
    "Take photo": "Kumuha ng litrato",
    "Choose a saved photo": "Pumili ng naka-save na litrato",
    "Use live camera": "Gamitin ang live camera",
    "Selected mango photo": "Napiling litrato ng mangga",
    "Change photo": "Palitan ang litrato",
    "Check this mango": "Suriin ang manggang ito",
    "Live camera view": "Live na view ng camera",
    "Mango inside the corners": "Ilagay ang mangga sa loob ng mga sulok",
    "Capture and check": "Kunan at suriin",
    "The live camera needs a secure (HTTPS) link. The normal camera still works:":
        "Kailangan ng live camera ang secure (HTTPS) na link. Gumagana pa rin ang karaniwang camera:",
    "Take photo instead": "Kumuha na lang ng litrato",
    "Back to photo": "Bumalik sa litrato",
    "You can also drop a photo on this page.": "Puwede ring i-drop ang litrato sa pahinang ito.",
    "JPG, PNG or WEBP, up to 10 MB.": "JPG, PNG o WEBP, hanggang 10 MB.",
    "Example photo": "Halimbawang litrato",
    "How MangoScan checks a photo": "Paano sinusuri ng MangoScan ang litrato",
    "It measures 32,795 colour, texture and shape values from the peel, then a trained model picks one of three answers.":
        "Sinusukat nito ang 32,795 na halaga ng kulay, tekstura at hugis mula sa balat, saka pipili ang isang sinanay na modelo ng isa sa tatlong sagot.",
    "Checking the peel": "Sinusuri ang balat",
    "The camera is still starting. Try again in a second.":
        "Nagsisimula pa ang camera. Subukan ulit pagkalipas ng isang segundo.",
    "Checking…": "Sinusuri…",
    "Camera not available ({reason}). The normal camera still works:":
        "Hindi magamit ang camera ({reason}). Gumagana pa rin ang karaniwang camera:",
    "permission denied": "hindi pinayagan",
    "That file is not a JPG, PNG or WEBP photo. Pick another one.":
        "Hindi JPG, PNG o WEBP na litrato ang file na iyan. Pumili ng iba.",
    "That photo is too large. Pick a smaller one or take a new photo.":
        "Masyadong malaki ang litrato. Pumili ng mas maliit o kumuha ng bago.",
    "Preparing photo…": "Inihahanda ang litrato…",
    "Take or choose a photo first.": "Kumuha o pumili muna ng litrato.",

    # ---------- Pipeline ----------
    "Resize photo": "Paliitin ang litrato",
    "HSV colour histogram": "HSV histogram ng kulay",
    "GLCM texture": "GLCM na tekstura",
    "Hu shape moments": "Hu shape moments",
    "RBF SVM decides": "Nagpapasya ang RBF SVM",
    "3 classes": "3 klase",

    # ---------- Result screen ----------
    "Verdict:": "Resulta:",
    "No disease found": "Walang nakitang sakit",
    "Disease found": "May nakitang sakit",
    "Healthy": "Malusog",
    "Ship it.": "Ipadala na.",
    "Quarantine.": "Ihiwalay.",
    "Trim the stem.": "Putulin ang tangkay.",
    "Fruit approved for commercial distribution, packaging, and long-term storage.":
        "Puwede nang ibenta, i-empake, at itago nang matagal ang bunga.",
    "Quarantine fruit. Apply postharvest hot water treatment (48 °C for 20 min) or prochloraz dip.":
        "Ihiwalay ang bunga. Pagkatapos anihin, ibabad sa mainit na tubig (48 °C sa loob ng 20 minuto) o isawsaw sa prochloraz.",
    "Trim stem flush with fruit shoulder. Separate from export crates and store in dry ventilation (below 13 °C).":
        "Putulin ang tangkay kapantay ng balikat ng bunga. Ihiwalay sa mga kahon para sa export at itago sa tuyo at mahanging lugar (mas mababa sa 13 °C).",
    "Scan another mango": "Mag-scan ng ibang mangga",
    "Saved to your scans": "Naka-save sa iyong mga scan",
    "See all": "Tingnan lahat",
    "{login} or {signup} to save your scans.": "{login} o {signup} para ma-save ang iyong mga scan.",
    "create an account": "gumawa ng account",
    "Photo evidence": "Litratong ebidensya",
    "Photo view": "Tingin sa litrato",
    "Marked up": "May marka",
    "Original": "Orihinal",
    "Photo of the mango with detected defect regions boxed": "Litrato ng mangga na may kahon sa mga nakitang sira",
    "Original photo of the mango": "Orihinal na litrato ng mangga",
    "Readings": "Mga sukat",
    "Grade": "Grado",
    "Export quality": "Pang-export na kalidad",
    "Infected specimen (cull)": "May sakit (itapon)",
    "Vascular tissue decay": "Nabubulok malapit sa tangkay",
    "Defect coverage": "Lawak ng sira",
    "of surface": "ng balat",
    "(clear surface)": "(malinis ang balat)",
    "of stem shoulder": "ng balikat ng tangkay",
    "Technical details": "Teknikal na detalye",
    "Model confidence": "Kumpiyansa ng modelo",
    "Mean hue": "Karaniwang hue",
    "Saturation": "Saturation",
    "Photo size": "Laki ng litrato",
    "How MangoScan read this fruit: 32,795 colour, texture and shape values, then a trained model picked the answer.":
        "Paano binasa ng MangoScan ang bungang ito: 32,795 na halaga ng kulay, tekstura at hugis, saka pumili ng sagot ang isang sinanay na modelo.",
    "Coverage is an Otsu-threshold estimate of dark peel area, not a lab measurement.":
        "Ang lawak ng sira ay tantya ng madilim na bahagi ng balat gamit ang Otsu threshold, hindi sukat mula sa laboratoryo.",
    "Delete this scan": "Burahin ang scan na ito",
    "Delete this scan?": "Burahin ang scan na ito?",
    "The photos and the reading will be removed from My scans. You can't undo this.":
        "Mabubura sa Aking mga scan ang mga litrato at ang resulta. Hindi na ito maibabalik.",
    "Cancel": "Kanselahin",
    "Delete scan": "Burahin ang scan",
    "Deleting…": "Binubura…",

    # ---------- Account forms ----------
    "Log in.": "Mag-log in.",
    "Your scans are saved to your account, so you can find them again on any phone.":
        "Naka-save ang iyong mga scan sa iyong account, kaya makikita mo ulit ang mga ito sa kahit anong phone.",
    "Email": "Email",
    "Password": "Password",
    "Create an account": "Gumawa ng account",
    "Forgot password?": "Nakalimutan ang password?",
    "You can scan without an account.": "Puwede kang mag-scan kahit walang account.",
    "Create an account.": "Gumawa ng account.",
    "Free. Every mango you scan is saved, with its photo and what to do.":
        "Libre. Naka-save ang bawat manggang ini-scan mo, kasama ang litrato at ang dapat gawin.",
    "Full name": "Buong pangalan",
    "At least 8 characters.": "Hindi bababa sa 8 karakter.",
    "Create account": "Gumawa ng account",
    "I already have an account": "May account na ako",
    "Forgot your password?": "Nakalimutan ang password?",
    "Enter your email. We will send a link to set a new password.":
        "Ilagay ang iyong email. Magpapadala kami ng link para gumawa ng bagong password.",
    "Send the link": "Ipadala ang link",
    "Back to log in": "Bumalik sa pag-log in",
    "Set a new password.": "Gumawa ng bagong password.",
    "For {email}.": "Para sa {email}.",
    "New password": "Bagong password",
    "Save password": "I-save ang password",
    "Show": "Ipakita",
    "Hide": "Itago",
    "Please wait…": "Sandali lang…",
    "Saving…": "Sine-save…",
    "Logging out…": "Nagla-log out…",
    "Notifications": "Mga abiso",
    "To confirm, type {word} below.": "Para kumpirmahin, i-type ang {word} sa ibaba.",
    "Capital letters do not matter.": "Hindi mahalaga kung malaki o maliit ang titik.",
    "What you typed does not match. Your account was not deleted.":
        "Hindi tugma ang na-type mo. Hindi nabura ang iyong account.",
    "Confirming": "Kinukumpirma",
    "One moment.": "Sandali lang.",
    "This link does not work.": "Hindi gumagana ang link na ito.",
    "It may have expired or been used already. Log in, or ask for a new link.":
        "Maaaring expired na o nagamit na ito. Mag-log in, o humingi ng bagong link.",
    "Get a new link": "Kumuha ng bagong link",

    # ---------- My scans ----------
    "My scans.": "Aking mga scan.",
    "Your scans could not be loaded. Check the connection and reload the page.":
        "Hindi ma-load ang iyong mga scan. Tingnan ang koneksyon at i-reload ang pahina.",
    "No saved scans yet.": "Wala pang naka-save na scan.",
    "Every mango you check while logged in shows up here.":
        "Lalabas dito ang bawat manggang susuriin mo habang naka-log in.",
    "Disease": "May sakit",
    "Log out": "Mag-log out",
    "Delete my account": "Burahin ang aking account",
    "Delete your account?": "Burahin ang iyong account?",
    "Your account, all your saved scans and their photos will be deleted for good. You can't undo this.":
        "Permanenteng mabubura ang iyong account, lahat ng naka-save na scan at ang mga litrato nito. Hindi na ito maibabalik.",
    "Delete account": "Burahin ang account",

    # ---------- Settings ----------
    "Settings": "Settings",
    "Language, app install and your account.": "Wika, pag-install ng app at ang iyong account.",
    "Choose the language MangoScan uses on this phone.": "Piliin ang wikang gagamitin ng MangoScan sa phone na ito.",
    "Install MangoScan": "I-install ang MangoScan",
    "Add MangoScan to your home screen so it opens like an app.":
        "Idagdag ang MangoScan sa home screen para bumukas ito na parang app.",
    "Add to home screen": "Idagdag sa home screen",
    "MangoScan is installed on this phone.": "Naka-install na ang MangoScan sa phone na ito.",
    "In your browser menu, tap “Add to Home screen” or “Install app”. On iPhone, tap Share, then “Add to Home Screen”.":
        "Sa menu ng browser, i-tap ang “Add to Home screen” o “Install app”. Sa iPhone, i-tap ang Share, saka “Add to Home Screen”.",
    "Profile": "Profile",
    "Signed in as {email}.": "Naka-log in bilang {email}.",
    "Save name": "I-save ang pangalan",
    "Enter your current password, then the new one.": "Ilagay ang kasalukuyang password, saka ang bago.",
    "Current password": "Kasalukuyang password",
    "Change password": "Palitan ang password",
    "Log out of MangoScan on this phone.": "Mag-log out sa MangoScan sa phone na ito.",
    "Permanently delete your account, all saved scans and their photos.":
        "Permanenteng burahin ang iyong account, lahat ng naka-save na scan at ang mga litrato nito.",
    "Account": "Account",
    "Log in to save your scans and find them again on any phone. Scanning works without an account.":
        "Mag-log in para ma-save ang iyong mga scan at makita ulit sa kahit anong phone. Puwedeng mag-scan kahit walang account.",
    "Use 100 characters or fewer.": "Gumamit ng hindi hihigit sa 100 karakter.",
    "Your name is saved.": "Naka-save na ang iyong pangalan.",
    "Enter your current password.": "Ilagay ang iyong kasalukuyang password.",
    "That password is not right.": "Mali ang password na iyan.",

    "Preferences": "Mga kagustuhan",
    "Install": "I-install",
    "Change the password you log in with.": "Palitan ang password na ginagamit mo sa pag-log in.",
    "Change": "Palitan",
    "Save your scans": "I-save ang iyong mga scan",
    "Danger zone": "Mapanganib na bahagi",

    "General": "Pangkalahatan",
    "saved scan": "naka-save na scan",
    "saved scans": "naka-save na scan",
    "Install app": "I-install ang app",
    "Browser menu → “Add to Home screen”": "Menu ng browser → “Add to Home screen”",
    "Installed": "Naka-install",
    "Name": "Pangalan",
    "Log in or create an account": "Mag-log in o gumawa ng account",
    "Save your scans and see them on any phone.": "I-save ang iyong mga scan at makita sa kahit anong phone.",
    "Deletes your account, all saved scans and their photos.": "Buburahin ang iyong account, lahat ng naka-save na scan at ang mga litrato nito.",

    # ---------- Offline ----------
    "No connection": "Walang koneksyon",
    "No internet connection.": "Walang koneksyon sa internet.",
    "MangoScan needs the internet to check a photo. Move to a place with signal, then try again.":
        "Kailangan ng MangoScan ang internet para suriin ang litrato. Lumipat sa lugar na may signal, saka subukan ulit.",
    "Try again": "Subukan ulit",

    # ---------- Server messages: scanning ----------
    "You have scanned a lot in a short time. Wait a few minutes, then try again.":
        "Marami ka nang na-scan sa maikling oras. Maghintay ng ilang minuto, saka subukan ulit.",
    "The camera photo could not be read. Try again.": "Hindi mabasa ang litrato mula sa camera. Subukan ulit.",
    "No photo selected. Take or choose a photo of one mango.":
        "Walang napiling litrato. Kumuha o pumili ng litrato ng isang mangga.",
    "That file type is not supported. Use a JPG, PNG or WEBP photo.":
        "Hindi suportado ang ganitong file. Gumamit ng JPG, PNG o WEBP na litrato.",
    "Take or choose a photo of one mango first.": "Kumuha o pumili muna ng litrato ng isang mangga.",
    "This file could not be opened as a photo. Choose another one.":
        "Hindi mabuksan ang file na ito bilang litrato. Pumili ng iba.",
    "We could not find a mango in this photo. Take a closer photo of one fruit on a plain background.":
        "Walang nakitang mangga sa litrato. Kumuha ng mas malapit na litrato ng isang bunga sa payak na background.",
    "This photo is too blurry. Hold the phone still and tap the mango to focus, then try again.":
        "Malabo ang litrato. Huwag galawin ang phone at i-tap ang mangga para mag-focus, saka subukan ulit.",
    "This photo is too dark. Move to brighter light and try again.":
        "Masyadong madilim ang litrato. Lumipat sa mas maliwanag na lugar at subukan ulit.",
    "This photo is too bright. Move out of direct glare and try again.":
        "Masyadong maliwanag ang litrato. Umiwas sa direktang sikat ng araw at subukan ulit.",
    "MangoScan is not set up correctly: the model files are missing.":
        "Hindi maayos ang setup ng MangoScan: nawawala ang mga file ng modelo.",
    "Something went wrong while checking this photo. Try again.":
        "May nagkaproblema habang sinusuri ang litrato. Subukan ulit.",
    "That photo is too large (over 10 MB). Choose a smaller one or take a new photo.":
        "Masyadong malaki ang litrato (lampas 10 MB). Pumili ng mas maliit o kumuha ng bago.",

    # ---------- Server messages: accounts ----------
    "That email and password do not match. Check them and try again.":
        "Hindi tugma ang email at password. Tingnan at subukan ulit.",
    "Confirm your email first. Open the link we sent to your inbox.":
        "Kumpirmahin muna ang iyong email. Buksan ang link na ipinadala namin sa iyong inbox.",
    "An account with this email already exists. Log in instead.":
        "May account na ang email na ito. Mag-log in na lang.",
    "Choose a stronger password: at least {n} characters.":
        "Pumili ng mas matibay na password: hindi bababa sa {n} karakter.",
    "Too many tries. Wait a minute, then try again.":
        "Masyadong maraming subok. Maghintay ng isang minuto, saka subukan ulit.",
    "Too many tries. Wait a few minutes, then try again.":
        "Masyadong maraming subok. Maghintay ng ilang minuto, saka subukan ulit.",
    "This link has expired or was already used. Ask for a new one.":
        "Expired na o nagamit na ang link na ito. Humingi ng bago.",
    "Something went wrong on our side. Try again in a moment.":
        "May nagkaproblema sa aming panig. Subukan ulit mamaya.",
    "Enter your name.": "Ilagay ang iyong pangalan.",
    "Enter an email address like name@example.com.": "Maglagay ng email na tulad ng name@example.com.",
    "Use at least {n} characters.": "Gumamit ng hindi bababa sa {n} karakter.",
    "Welcome, {name}. Your scans will now be saved.": "Maligayang pagdating, {name}. Mase-save na ang iyong mga scan.",
    "Check your email": "Tingnan ang iyong email",
    "Check your email.": "Tingnan ang iyong email.",
    "We sent a link to {email}. Open it to confirm your account, then log in.":
        "Nagpadala kami ng link sa {email}. Buksan ito para kumpirmahin ang iyong account, saka mag-log in.",
    "Enter the email you signed up with.": "Ilagay ang email na ginamit mo sa pag-sign up.",
    "Enter your password.": "Ilagay ang iyong password.",
    "You are logged out.": "Naka-log out ka na.",
    "If {email} has an account, we sent a link to set a new password.":
        "Kung may account ang {email}, nagpadala kami ng link para gumawa ng bagong password.",
    "We just sent you an email. Wait {n} seconds before asking for another one.":
        "Kapapadala lang namin ng email. Maghintay ng {n} segundo bago humingi ng panibago.",
    "We have sent too many emails for now. Try again in an hour.":
        "Masyadong marami na ang naipadalang email sa ngayon. Subukan ulit pagkalipas ng isang oras.",
    "Send the email again": "Ipadala ulit ang email",
    "No email after a few minutes? Check your spam folder, or send it again.":
        "Wala pa ring email pagkalipas ng ilang minuto? Tingnan ang spam folder, o ipadala ulit.",
    "We sent a new link to {email}. Open the newest email to confirm your account, then log in.":
        "Nagpadala kami ng bagong link sa {email}. Buksan ang pinakabagong email para kumpirmahin ang iyong account, saka mag-log in.",
    "We could not send the email right now. Try again later, or contact the MangoScan team.":
        "Hindi namin maipadala ang email ngayon. Subukan ulit mamaya, o makipag-ugnayan sa MangoScan team.",
    "Link not valid": "Hindi wasto ang link",
    "Open the newest email from MangoScan, or ask for a new link.":
        "Buksan ang pinakabagong email mula sa MangoScan, o humingi ng bagong link.",
    "Your email is confirmed. Your scans will now be saved.":
        "Nakumpirma na ang iyong email. Mase-save na ang iyong mga scan.",
    "Your new password is saved.": "Naka-save na ang iyong bagong password.",
    "Scan deleted.": "Nabura na ang scan.",
    "That scan could not be deleted. Try again.": "Hindi mabura ang scan. Subukan ulit.",
    "Your account could not be deleted. Try again, or contact the MangoScan team.":
        "Hindi mabura ang iyong account. Subukan ulit, o makipag-ugnayan sa MangoScan team.",
    "Your account and all your saved scans were deleted.":
        "Nabura na ang iyong account at lahat ng naka-save na scan.",
    "The form expired. Go back, reload the page and try again.":
        "Nag-expire ang form. Bumalik, i-reload ang pahina at subukan ulit.",
    "Something was not right.": "May hindi tama.",
    "Page not found.": "Hindi nakita ang pahina.",
    "Not available yet.": "Hindi pa available.",
    "Something went wrong.": "May nagkaproblema.",
    "The page or scan you asked for does not exist.": "Walang ganitong pahina o scan.",

    # ---------- Screen guides ----------
    "Show how this screen works": "Ipakita kung paano gamitin ang screen na ito",
    "Skip guide": "Laktawan",
    "Back": "Bumalik",
    "Next": "Susunod",
    "Got it": "Sige, gets ko",
    "Step {n} of {total}": "Hakbang {n} sa {total}",
    "Help on every screen": "May tulong sa bawat screen",
    "Tap the question mark at the top to see the guide for any screen again.":
        "Pindutin ang tandang pananong sa itaas para makita ulit ang gabay ng kahit anong screen.",
    # Landing
    "Start here": "Dito magsimula",
    "Tap Scan a mango to check a fruit. It is free and you do not need an account.":
        "Pindutin ang I-scan ang mangga para suriin ang isang bunga. Libre ito at hindi kailangan ng account.",
    "One of three answers": "Isa sa tatlong sagot",
    "MangoScan tells you if a mango is healthy, has anthracnose or has stem-end rot, and what to do with it.":
        "Sasabihin ng MangoScan kung ang mangga ay malusog, may anthracnose o may stem-end rot, at kung ano ang gagawin dito.",
    "Language and app": "Wika at app",
    "Tap the gear to switch to Filipino or put MangoScan on your home screen.":
        "Pindutin ang gear para lumipat sa Filipino o ilagay ang MangoScan sa home screen mo.",
    # Scan
    "Keep the mango inside the corners": "Panatilihin ang mangga sa loob ng mga sulok",
    "Hold the phone still so the whole fruit fits inside the four corners.":
        "Hawakan nang steady ang phone para magkasya ang buong bunga sa loob ng apat na sulok.",
    "Tap once. MangoScan takes the photo and checks it right away.":
        "Pindutin nang isang beses. Kukunan ito ng MangoScan at susuriin agad.",
    "Tap here to open your camera. Take one mango so it fills the photo.":
        "Pindutin dito para buksan ang camera. Kunan ang isang mangga nang punô ang litrato.",
    "For a clear answer": "Para sa malinaw na sagot",
    "Use a plain background and even light, with the stem end showing. If the photo is blurry or too dark, MangoScan asks for a new one.":
        "Gumamit ng simpleng background at pantay na liwanag, at ipakita ang dulo ng tangkay. Kung malabo o masyadong madilim ang litrato, hihingi ang MangoScan ng bago.",
    "Already have a photo?": "May litrato ka na?",
    "Pick a mango photo from your phone's gallery instead.":
        "Pumili na lang ng litrato ng mangga mula sa gallery ng phone mo.",
    "Live camera": "Live camera",
    "Aim at the mango and capture it here, without leaving the page.":
        "Itutok sa mangga at kunan dito mismo, nang hindi umaalis sa pahina.",
    # Result
    "The answer": "Ang sagot",
    "This is what MangoScan found. The lines below it say what to do with the fruit.":
        "Ito ang nakita ng MangoScan. Sinasabi ng mga linya sa ibaba kung ano ang gagawin sa bunga.",
    "Your photo, marked": "Ang litrato mo, may marka",
    "The green frame shows the fruit MangoScan checked. Tap Original to see your photo without marks.":
        "Ipinapakita ng berdeng frame ang bungang sinuri ng MangoScan. Pindutin ang Orihinal para makita ang litrato nang walang marka.",
    "The boxes show where MangoScan found bad spots. Tap Original to see your photo without marks.":
        "Ipinapakita ng mga kahon kung saan may nakitang sira ang MangoScan. Pindutin ang Orihinal para makita ang litrato nang walang marka.",
    "Grade and coverage": "Grado at lawak ng sira",
    "Grade A is good to sell. Grade C needs sorting or treatment. Coverage is about how much of the peel looks affected.":
        "Ang Grado A ay puwedeng ibenta. Ang Grado C ay kailangang ihiwalay o gamutin. Ang lawak ng sira ay tantiya kung gaano karami ng balat ang apektado.",
    "Saved to My scans": "Naka-save sa Aking mga scan",
    "Keep your results": "I-save ang iyong mga resulta",
    "You can open this result again any time from My scans.":
        "Mabubuksan mo ulit ang resultang ito anumang oras mula sa Aking mga scan.",
    "Log in or create a free account, and every mango you check is saved.":
        "Mag-log in o gumawa ng libreng account, at mase-save ang bawat manggang susuriin mo.",
    "Next mango": "Susunod na mangga",
    "Tap here to check another fruit.": "Pindutin dito para sumuri ng isa pang bunga.",
    # My scans
    "Your saved scans": "Ang iyong mga naka-save na scan",
    "Newest first. Tap a scan to see its photo and what to do again.":
        "Pinakabago ang nasa itaas. Pindutin ang isang scan para makita ulit ang litrato at ang dapat gawin.",
    "Mangoes with a disease are marked, so you can find them quickly.":
        "May marka ang mga manggang may sakit, para madali mo silang makita.",
    "Nothing saved yet": "Wala pang naka-save",
    "Every mango you check while logged in shows up here, with its photo.":
        "Lalabas dito ang bawat manggang susuriin mo habang naka-log in, kasama ang litrato nito.",
    "Check a mango": "Sumuri ng mangga",
    "Start a new scan from here.": "Magsimula ng bagong scan dito.",
    # Settings
    "Choose English or Filipino. This phone remembers your choice.":
        "Pumili ng English o Filipino. Tatandaan ito ng phone na ito.",
    "Put MangoScan on your phone": "Ilagay ang MangoScan sa phone mo",
    "Add it to your home screen and it opens like an app, straight to scanning.":
        "Idagdag ito sa home screen at bubukas ito na parang app, diretso sa pag-scan.",
    "These guides": "Ang mga gabay na ito",
    "Turn the guides off here, or show them all again.":
        "Dito mo mapapatay ang mga gabay, o maipapakita ulit lahat.",
    "Your data": "Ang iyong data",
    "You can delete your account, every saved scan and every photo at any time.":
        "Puwede mong burahin ang iyong account, bawat naka-save na scan at bawat litrato anumang oras.",
    "Log in or create a free account to keep every result.":
        "Mag-log in o gumawa ng libreng account para ma-save ang bawat resulta.",
    "Screen guides": "Mga gabay sa screen",
    "On this phone": "Sa phone na ito",
    "Show how each screen works, the first time": "Ipakita kung paano gamitin ang bawat screen, sa unang beses",
    "Opens like an app from your home screen": "Bubukas na parang app mula sa home screen",
    "Not set": "Wala pa",
    "A short guide shows how each screen works the first time you open it.":
        "May maikling gabay na nagpapakita kung paano gamitin ang bawat screen sa unang beses mo itong buksan.",
    "On": "Bukas",
    "Off": "Sarado",
    "Show all guides again": "Ipakita ulit lahat ng gabay",
    "Guides are on. Each screen shows its guide the first time.":
        "Bukas ang mga gabay. Ipapakita ng bawat screen ang gabay nito sa unang beses.",
    "Guides are off. Tap the question mark on any screen to see its guide.":
        "Sarado ang mga gabay. Pindutin ang tandang pananong sa kahit anong screen para makita ang gabay nito.",
    "Every screen will show its guide again.": "Ipapakita ulit ng bawat screen ang gabay nito.",
    # Account screens
    "Use the email and password you signed up with. Tap Show to check what you typed.":
        "Gamitin ang email at password na ginamit mo sa pag-sign up. Pindutin ang Ipakita para makita ang tinype mo.",
    "Tap here and we email you a link to make a new one.":
        "Pindutin dito at magpapadala kami ng link sa email para gumawa ng bago.",
    "New to MangoScan?": "Bago ka sa MangoScan?",
    "Create a free account here. You can also scan without one.":
        "Gumawa ng libreng account dito. Puwede ka ring mag-scan kahit wala nito.",
    "Three things to fill in": "Tatlong kailangang punan",
    "Your name, your email, and a password of at least 8 characters.":
        "Ang pangalan mo, ang email mo, at password na may hindi bababa sa 8 karakter.",
    "Then check your email": "Pagkatapos, tingnan ang email mo",
    "After you tap Create account, open the link we email you. Your account is ready once you do.":
        "Pagkapindot mo ng Gumawa ng account, buksan ang link na ipapadala namin sa email. Handa na ang account mo kapag nagawa mo ito.",
    "Get a new password": "Kumuha ng bagong password",
    "Enter the email you signed up with. If the email does not arrive in a few minutes, check your spam folder.":
        "Ilagay ang email na ginamit mo sa pag-sign up. Kung hindi dumating ang email sa loob ng ilang minuto, tingnan ang spam folder.",
    "Choose a new password": "Pumili ng bagong password",
    "Use at least 8 characters. After you save it, you stay logged in.":
        "Gumamit ng hindi bababa sa 8 karakter. Pagka-save, mananatili kang naka-log in.",
    "Open your email": "Buksan ang email mo",
    "Find the email from MangoScan and tap the link in it. It can take a few minutes to arrive.":
        "Hanapin ang email mula sa MangoScan at pindutin ang link dito. Maaaring abutin ng ilang minuto bago ito dumating.",
    "No email?": "Walang email?",
    "Check your spam folder first. Still nothing after a minute? Tap here to send it again.":
        "Tingnan muna ang spam folder. Wala pa rin pagkalipas ng isang minuto? Pindutin dito para ipadala ulit.",
}


def current_lang():
    lang = g.get("lang")
    if lang:
        return lang
    lang = request.cookies.get(COOKIE)
    if lang not in LANGS:
        accept = (request.headers.get("Accept-Language") or "").lower()
        lang = "fil" if accept.startswith(("fil", "tl")) else "en"
    g.lang = lang
    return lang


def t(text, **values):
    """Translate an English string into the visitor's language, then fill in {placeholders}."""
    out = FIL.get(text, text) if current_lang() == "fil" else text
    return out.format(**values) if values else out


def t_html(text, **values):
    """Like t(), for trusted strings that carry markup; placeholders are escaped unless already Markup."""
    out = FIL.get(text, text) if current_lang() == "fil" else text
    return Markup(out).format(**values) if values else Markup(out)


@bp.record_once
def _register(state):
    # Globals rather than context, so macros imported with {% from ... import %} see them too
    state.app.jinja_env.globals.update(_=t, _html=t_html)


@bp.app_context_processor
def _template_globals():
    return {"lang": current_lang()}


@bp.route("/lang/<code>")
def set_lang(code):
    if code not in LANGS:
        code = "en"
    nxt = request.args.get("next", "")
    if not (nxt.startswith("/") and not nxt.startswith("//") and "\\" not in nxt):
        nxt = url_for("index")
    resp = redirect(nxt)
    resp.set_cookie(COOKIE, code, max_age=365 * 24 * 3600, samesite="Lax", secure=request.is_secure)
    return resp

# קריית יראנו ניסים — חבילת פרומפטים להדמיות פוטוריאליסטיות

## איך משתמשים — 3 דקות הכנה

**הכלי המומלץ:** Midjourney (הכי פוטוריאליסטי לאדריכלות). חלופות חינמיות טובות: **Ideogram.ai**, **Leonardo.ai**, או **Bing Image Creator** (של מיקרוסופט, חינם לגמרי).

1. היכנס לכלי, פתח יצירת תמונה חדשה
2. העתק פרומפט שלם מהרשימה למטה (כולל הפרמטרים בסוף) והדבק
3. ב-Midjourney: הפקודה היא `/imagine` ואז הדבקה. בכלים אחרים: פשוט מדביקים בתיבה
4. כל פרומפט מפיק 4 וריאציות — בחר את הטובה ולחץ Upscale

**שלושה כללים חשובים:**
- **עקביות:** כל הפרומפטים פותחים באותו "DNA של הבניין" — כך המגדל ייראה אותו בניין בכל התמונות. ב-Midjourney, אחרי שיש תמונה ראשונה שאהבת — הוסף את הקישור שלה עם `--sref` לפרומפטים הבאים והבניין יישמר זהה
- **בלי טקסט עברי בתמונה:** מחוללי AI משבשים אותיות עבריות. הפרומפטים כוללים "no text, no signage" — את הלוגו והכיתוב נוסיף אחר כך בעריכה
- **יחס תמונה:** לתמונת מגדל אנכית `--ar 3:4`, לפנים רחבים `--ar 16:9` (בכלים בלי פרמטרים — בחר Portrait/Landscape בממשק)

---

## ה-DNA של הבניין (מופיע בכל פרומפט)

> a modern 14-story landmark tower in Netanya Israel: three-story Jerusalem-stone podium with five tall arched windows glowing warm gold (center arch largest), monumental entrance portal with brass canopy; slender tower of deep navy-blue glass with vertical brass fins, one mid-height floor glowing warm gold; rooftop wooden pergola terrace with warm string lights

---

## פרומפט 1 · תמונת הדגל — המגדל בשעה הכחולה

```
Award-winning architectural photography, hero shot at blue hour, a modern 14-story landmark tower in Netanya Israel: three-story Jerusalem-stone podium with five tall arched windows glowing warm gold (center arch largest), monumental entrance portal with brass canopy; slender tower of deep navy-blue glass with vertical brass fins, one mid-height floor glowing warm gold; rooftop wooden pergola terrace with warm string lights. Wet street reflections, warm interior light spilling out, a few people walking toward the entrance, Mediterranean coastal city in background, cinematic lighting, ultra photorealistic, shot on Phase One 150MP, 8k, no text, no signage --ar 3:4 --style raw --v 6.1
```

## פרומפט 2 · הכניסה הראשית מגובה רחוב

```
Street-level architectural photography at dusk, monumental entrance of a modern Jewish study center: Jerusalem-stone facade, tall brass-framed glass portal with warm light inside, brass canopy above, five grand arched windows glowing gold on the floors above, young men in white shirts entering, warm and welcoming atmosphere, ultra photorealistic, 8k, shallow depth of field, no text, no signage --ar 16:9 --style raw --v 6.1
```

## פרומפט 3 · היכל בית המדרש הגדול (פנים)

```
Interior architectural photography of a grand double-height Jewish study hall (beit midrash): soaring 12-meter ceiling, towering gilded Torah ark of dark walnut and gold at the far wall with glowing curtain, central raised bima platform with brass rails, hundreds of wooden study lecterns (shtenders) with open Talmud volumes, young men studying in pairs with animated hand gestures, massive brass chandeliers, warm golden light mixing with cool daylight from tall arched windows, upper gallery balcony, Jerusalem stone columns, ultra photorealistic, architectural digest style, 8k, no text --ar 16:9 --style raw --v 6.1
```

## פרומפט 4 · אולם ההרצאות התת-קרקעי

```
Interior photography of a modern underground auditorium in a Jewish community tower: 500 upholstered seats in navy blue facing a wide stage with warm gold accent lighting, elegant wraparound mezzanine gallery with lattice screen, acoustic wood-slat walls with brass trim, dramatic recessed ceiling lighting, a rabbi speaking on stage to a full crowd of men, warm inspiring atmosphere, ultra photorealistic, 8k, no text --ar 16:9 --style raw --v 6.1
```

## פרומפט 5 · לובי ההייטק עם הכולל

```
Interior photography of a luxurious hi-tech lobby in a religious landmark tower: polished Jerusalem stone and brass finishes, floor-to-ceiling LED media wall with soft golden abstract light patterns, modern reception desk, and through a full-height glass wall — a warm study hall where Torah scholars learn at wooden tables, blend of cutting-edge technology and ancient tradition, ultra photorealistic, 8k, no text, no signage --ar 16:9 --style raw --v 6.1
```

## פרומפט 6 · חופה על הגג בשקיעה

```
Rooftop wedding ceremony photography at golden sunset over the Mediterranean sea: elegant white chuppah canopy on a wooden pergola terrace atop a modern tower, warm string lights, guests in festive attire, groom and bride silhouetted against orange sea horizon, Netanya coastline below, emotional warm cinematic light, ultra photorealistic, 8k --ar 16:9 --style raw --v 6.1
```

## פרומפט 7 · מבט אווירי על הקריה

```
Aerial drone photography at dusk of a 14-story landmark tower campus in Netanya Israel: navy-blue glass tower with golden-lit stone podium and five glowing arched windows, rooftop pergola terrace lit warmly, adjacent smaller community building, Mediterranean sea and city lights in background, ultra photorealistic, cinematic, 8k, no text --ar 16:9 --style raw --v 6.1
```

## פרומפט 8 · חדר פנימייה של הישיבה

```
Interior photography of a modern dormitory room for post-army yeshiva students: two quality wooden beds with navy bedding, large window with sea view, wooden desks with Hebrew religious books stacked (books closed, no readable text), warm minimal design with brass reading lamps, feels like a boutique hostel not an institution, ultra photorealistic, 8k --ar 16:9 --style raw --v 6.1
```

---

## אחרי שיש תמונות

1. בחר את הטובות — בדוק שהבניין עקבי בין התמונות (אם לא — השתמש ב-`--sref` עם התמונה הכי טובה)
2. שלח לי אותן — אני אשלב אותן במצגת kirya.html במקום/לצד האיורים, ונוסיף את הלוגו והכיתובים בעברית
3. לראש הישיבה מציגים: המצגת האינטראקטיבית + התמונות הפוטוריאליסטיות ביחד

*מסמך עבודה פנימי · קריית יראנו ניסים · נבנה על בסיס גרסה 3 של התוכנית*

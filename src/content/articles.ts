import type { Article, ReviewStatus } from './types';

const d: ReviewStatus = { status: 'draft', reviewer: null, review_date: null };
const dv: ReviewStatus = { status: 'draft', reviewer: null, review_date: null, varies_by_nuu: true };

export const articles: Article[] = [
  {
    id: 'faamatai-overview',
    title_en: 'What is the Fa\'amatai?',
    title_sm: "O le ā le Fa'amatai?",
    eyebrow_en: 'Fa\'amatai',
    eyebrow_sm: 'Fa\'amatai',
    body_en:
      "The fa'amatai is the chiefly system that organises Samoan family and village life. Every aiga has matai — title-holders responsible for the family, its lands, and its standing. Every nu'u (village) has a fono — a council of its matai — which manages village affairs. The system rests on a single principle: O le ala i le pule o le tautua. The path to leadership is service.",
    body_sm:
      "O le fa'amatai o le faiga o le ta'ita'iga e fa'atulagaina ai le aiga ma le nu'u Sāmoa. E i ai matai o ia aiga ma ia aiga — e umia suafa, e fa'atautaia le aiga, ona fanua, ma lona mamalu. E i ai le fono a ia nu'u ma ia nu'u — o le aoao o matai e tausia le nu'u. O le faiga atoa e fa'avae i se mataupu silisili e tasi: O le ala i le pule o le tautua.",
    sections: [
      {
        step: 1,
        title_en: 'Ali\'i and Tulafale',
        title_sm: "Ali'i ma Tulafale",
        body_en:
          "Matai fall into two main classes. Ali'i carry the dignity and lineage of the title — they speak less but their word weighs more. Tulafale (orators) hold the speech rights of the aiga — they deliver lauga, manage protocol, and represent the ali'i in public exchange. Both are matai; neither is above the other. The system requires both.",
        body_sm:
          "E vaevaeina matai i ni vasega tetele e lua. O ali'i e fa'aali le mamalu ma le gafa o le suafa — e itiiti a latou tautalaga ae e mamafa. O tulafale e umia le tofi o le tautala — e fofogaina lauga, fa'atautaia tu, ma fai ma sui o ali'i i le tu'ufa'atasiga aloa'ia. E tutusa matai e lua — e leai se isi e sili. E mana'omia uma e le faiga.",
      },
      {
        step: 2,
        title_en: 'The aiga and the sa\'o',
        title_sm: 'O le aiga ma le sa\'o',
        body_en:
          "Every aiga has a sa'o — the head matai who carries the senior title. The sa'o has the authority to bestow titles, manage family land, and represent the aiga in the village fono. The sa'o consults the aiga potopoto on big decisions; they do not act alone.",
        body_sm:
          "E i ai le sa'o o ia aiga ma ia aiga — o le matai sili e umia le suafa maualuga. E iai le pule o le sa'o e tu'uina atu suafa, fa'atautaia fanua o le aiga, ma fai ma sui o le aiga i le fono a le nu'u. E fesili le sa'o i le aiga potopoto i fa'ai'uga tetele; e le tu'utu'u na'o ia.",
      },
      {
        step: 3,
        title_en: 'The fono and the nu\'u',
        title_sm: 'O le fono ma le nu\'u',
        body_en:
          "The village fono is the council of matai of a nu'u. It meets regularly. Matters of village discipline, fa'alavelave, church support, and visiting parties are handled here. Seating in the fono follows precise rank; speaking order follows from the host tulafale.",
        body_sm:
          "O le fono a le nu'u o le aoao o matai. E fono so'o. E fa'atautaia ai pulega o le nu'u, fa'alavelave, fesoasoani i le lotu, ma malo asiasi. E i ai le fa'asologa o le nofoa; e ta'imua e le tulafale o le aiga le fa'asologa o tautalaga.",
      },
    ],
    review: dv,
  },
  {
    id: 'how-titles-bestowed',
    title_en: 'How matai titles are bestowed',
    title_sm: 'O le fa\'apefea ona tu\'uina atu suafa matai',
    eyebrow_en: 'Fa\'amatai',
    eyebrow_sm: 'Fa\'amatai',
    body_en:
      "A matai title belongs to an aiga, not to an individual. When a title becomes vacant, the aiga potopoto meets — sometimes for months — to agree on a successor. The candidate is chosen on demonstrated tautua, character, knowledge, and ability to serve. Once chosen, the title is conferred at a saofa'i ceremony in front of the village fono. The bestowing of the title is also a fa'alavelave: 'ie toga, money, and food are presented to the village.",
    body_sm:
      "E i ai se suafa matai i totonu o se aiga, ae le i se tagata. Pe a avanoa se suafa, e fono le aiga potopoto — e o'o lava i ni masina — e malilie ai i se sui. E filifilia le sui i lana tautua, amio, poto, ma le mafai ona tausi. Pe a ua filifilia, e tu'uina atu le suafa i se sauniga saofa'i i luma o le fono a le nu'u. O le tu'uina atu o le suafa, o se fa'alavelave fo'i: e tu'uina atu 'ie tōga, tupe, ma mea'ai i le nu'u.",
    review: dv,
  },
  {
    id: 'faalavelave-overview',
    title_en: 'What is fa\'alavelave?',
    title_sm: 'O le ā le fa\'alavelave?',
    eyebrow_en: 'Fa\'alavelave',
    eyebrow_sm: 'Fa\'alavelave',
    body_en:
      "Fa'alavelave is both the event and the obligation it creates. A wedding, a funeral, a saofa'i, a graduation, a church dedication — each is a fa'alavelave to which the aiga must contribute. Contributions take three forms: 'ie toga, money, and food. The contribution honours the host; the host honours the giver by acknowledging publicly. Reciprocity is tracked — when the host has a fa'alavelave of their own, they will contribute in kind.",
    body_sm:
      "O le fa'alavelave o le sauniga ma le tiute e fa'atupuina. O se fa'aipoipoga, maliu, saofa'i, fa'au'uga, fa'apa'iaga o se falesa — o ia mea uma o ni fa'alavelave e mana'omia ai le fesoasoani a le aiga. E tolu vaega o fesoasoani: 'ie tōga, tupe, ma mea'ai. E fa'aaloalogia e le fesoasoani le aiga e talimalo; e fa'aaloalogia foi e le aiga le tagata na fesoasoani i le ta'uina aloa'ia. E manatua e le aiga le fesoasoani na maua — pe a fai sa latou fa'alavelave, e toe tu'uina atu se fesoasoani.",
    sections: [
      {
        step: 1,
        title_en: 'Types and weight of fa\'alavelave',
        title_sm: 'Ituaiga ma le mamafa o fa\'alavelave',
        body_en:
          "Not all fa'alavelave carry the same weight. A funeral typically demands the largest contribution. A first saofa'i, a wedding of an aiga's eldest, a church dedication — these are also heavy. A first birthday, a graduation — these are lighter but still meaningful. Speak to your matai to gauge what is appropriate.",
        body_sm:
          "E le tutusa le mamafa o fa'alavelave uma. O le maliu e masani lava ona sili ona mamafa. O le saofa'i muamua, o se fa'aipoipoga a le ulumatua o le aiga, o le fa'apa'iaga o se falesa — e mamafa fo'i. O se aso fanau muamua, o se fa'au'uga — e itiiti, ae tāua pea. Fesili i lou matai e iloa ai le mea talafeagai.",
      },
      {
        step: 2,
        title_en: 'How to deliver a contribution',
        title_sm: 'O le fa\'apefea ona tu\'uina atu se fesoasoani',
        body_en:
          "Money goes in an envelope, marked with the giver's name and aiga. 'Ie toga are folded carefully and laid out by a representative who names them aloud at the si'i. Food is prepared and brought ready to serve. Hand contributions to a tulafale of the receiving aiga or directly to the sa'o of the family — never leave them on a table unattended.",
        body_sm:
          "E tu'u le tupe i totonu o se teutusi ma le igoa o le tagata ma lona aiga. E gaugau ma le fa'aaloalo 'ie tōga ma fa'aali e se sui o le igoa i le si'i. E saunia mea'ai ma aumai ua sauni e tausi. Tu'uina atu fesoasoani i se tulafale o le aiga e talia po o tu'u sa'o atu i le sa'o o le aiga — aua ne'i tu'u i luga o se laulau.",
      },
      {
        step: 3,
        title_en: 'When you cannot contribute fully',
        title_sm: 'Pe a le mafai ona fa\'ataunu\'u atoatoa',
        body_en:
          "If circumstance means you cannot meet the expected contribution, communicate this directly to your matai or to the receiving aiga ahead of time. Use the word fa'atoesega — apology. Send what you can with respect. To send nothing without word is the failure; to send little with explanation is honoured.",
        body_sm:
          "Pe afai e le mafai ona fa'ataunu'u atoatoa le fesoasoani fa'amoemoeina, fa'ailoa atu sa'o lea i lou matai po o le aiga e talia, a'o le'i o'o le aso. Fa'aaogā le upu fa'atoesega. Tu'uina atu le mea e mafai ma le fa'aaloalo. O le le tu'uina atu ma le le fa'ailoa — o le sese lea; o le itiiti ma le fa'amatalaga — e fa'aaloalogia.",
      },
      {
        step: 4,
        title_en: 'Reciprocity',
        title_sm: 'Tāui o fesoasoani',
        body_en:
          "The aiga remembers. Each contribution received creates a known obligation. When that family later has their own fa'alavelave, your aiga is expected to respond. This is the rhythm of Samoan life — and the reason fa'alavelave is best understood as a long-running reciprocal relationship, not a one-off transaction.",
        body_sm:
          "E manatua e le aiga. E tupu se tiute mai ia fesoasoani ta'itasi. Pe a o'o i se fa'alavelave a le isi aiga, e fa'amoemoeina lou aiga e toe tu'uina atu. O le pa'ō lea o le ola Sāmoa — ma o le mafua'aga e malamalama ai i le fa'alavelave o se mafutaga umi e fa'afesoasoani, ae le i se fa'atauga e tasi.",
      },
      {
        step: 5,
        title_en: 'For the diaspora',
        title_sm: 'Mo i latou o lo\'o nofo i fafo',
        body_en:
          "Distance does not end fa'alavelave. Many diaspora Samoans send money via aiga in country; others fly back for weddings and funerals. Speak to your matai or sa'o about your obligations and capacity. Do not let silence speak for you — speak openly. Many aiga will adjust expectations for those overseas when communication is good.",
        body_sm:
          "E le mavae le fa'alavelave i le mamao. E tele tagata Sāmoa o lo'o nofo i fafo e tu'uina atu tupe e ala i aiga i Sāmoa; o nisi e folau atu i fa'aipoipoga ma maliu. Talanoa i lou matai po o le sa'o e uiga i au tiute ma le mafai. Aua le tu'u i le filemu e tautala mo oe — talanoa lava. E tele aiga e fetuuna'i fa'amoemoega mo i latou i fafo pe a lelei le talanoaga.",
      },
    ],
    review: dv,
  },
  {
    id: 'ietoga-guide',
    title_en: "'Ie Toga — Fine Mats",
    title_sm: "'Ie Tōga",
    eyebrow_en: 'Cultural Currency',
    eyebrow_sm: 'O le aganu\'u',
    body_en:
      "'Ie toga are finely woven mats made from the inner bast of the paogo (pandanus) leaf. A single 'ie toga can take months — sometimes years — to weave. They are not floor mats; they are the cultural currency of Samoa, presented at every fa'alavelave. The value of an 'ie toga reflects its age, its fineness of weave, its history (the named pieces are remembered), and the family that presents it.",
    body_sm:
      "O 'ie tōga o ni mea fofola e lalaga lelei mai i le pa'u o totonu o le lau o le paogo. E mafai ona fai i ni masina po o ni tausaga le lalaga o se tasi 'ie tōga. E le o ni fala fofola; o le mea taua o le aganu'u Sāmoa, e tu'uina atu i so'o se fa'alavelave. E faia le tāua o se 'ie tōga i lona tausaga, le lelei o le lalaga, lona tala'aga (e manatua 'ie tōga e i ai igoa), ma le aiga e tu'uina atu.",
    sections: [
      {
        step: 1,
        title_en: 'Grading and value',
        title_sm: 'Vasega ma le tāua',
        body_en:
          "The finest 'ie toga — known as 'ie o le mālō or named historic mats — are reserved for the heaviest fa'alavelave (state funerals, major saofa'i, royal exchanges). Most 'ie toga in family life are well-woven but not named, and circulate among aiga at weddings and funerals. Quality is judged by the tightness of weave, the fineness of the strips, and the condition of the edges.",
        body_sm:
          "O 'ie tōga sili — ua ta'ua o 'ie o le mālō po o 'ie ua i ai igoa — e teu mo fa'alavelave sili ona mamafa (maliu o le mālō, saofa'i tetele, fefa'asoaa'iga o le mālō). O le tele o 'ie tōga i le aiga e lalaga lelei ae leai ni igoa, e fa'afesoaina i le va o aiga i fa'aipoipoga ma maliu. E fa'avae le lelei i le mau o le lalaga, le lelei o le sili, ma le tulaga o le tafatafa.",
      },
      {
        step: 2,
        title_en: 'When to give and when to receive',
        title_sm: 'Tu\'uina atu ma talia',
        body_en:
          "If your aiga is hosting, you receive. If you are visiting as a contributing aiga, you give. The number given is read carefully — too few and the host will note it; too many and you may have overshot what the occasion calls for. Ask your sa'o before deciding alone.",
        body_sm:
          "Pe afai o lou aiga o lo'o talimalo, e talia. Pe afai e te asiasi e te fa'asaga ai, e tu'uina atu. E fuatia ma le tatau le aofa'i — pe afai e itiiti, e iloa e le aiga; pe afai e tele tele, e sili atu i le mea talafeagai. Fesili i lou sa'o a'o le'i fa'aiu na'o oe.",
      },
      {
        step: 3,
        title_en: 'Storage and care',
        title_sm: 'Teuga ma le tausiga',
        body_en:
          "'Ie toga are folded carefully — never crumpled — and stored flat or rolled in a dry place. Many aiga keep them in dedicated cloth wraps. Do not sit on, walk over, or place objects on an 'ie toga.",
        body_sm:
          "Gaugau lelei 'ie tōga — aua ne'i nono — ma teu i se nofoaga mago, gaugau pe ta'ai. E tele aiga e teu i totonu o ie fa'apitoa. Aua e te nofo, savali, po o tu'u so'o se mea i luga o se 'ie tōga.",
      },
    ],
    review: dv,
  },
  {
    id: 'dress-code',
    title_en: 'Dress Code by Event',
    title_sm: 'Lā\'ei e tusa ai ma le sauniga',
    eyebrow_en: 'Practical',
    eyebrow_sm: 'Aoga',
    body_en:
      "Samoan formal dress codes are clear and worth taking seriously. The wrong outfit at a saofa'i or funeral is not just a fashion mistake — it reads as disrespect. When in doubt, ask your aiga or err on the side of more covered, more formal, and darker.",
    body_sm:
      "E manino lā'ei aloa'ia Sāmoa ma e tāua le tausi. O se lā'ei sese i se saofa'i po o se maliu e le na o le sese o le lā'ei — e iloa o le le fa'aaloalo. Pe a masalo, fesili i lou aiga, po o le fai i se mea ua ufiufi, aloa'ia, ma pogisa.",
    sections: [
      {
        step: 1,
        title_en: 'Church and Sunday',
        title_sm: 'Lotu ma le Aso Sa',
        body_en:
          "Women: puletasi or long modest dress; head covered (a hat or scarf) for the service. Men: ie faitaga and white shirt with tie, or full suit. Children: clean and tucked in; girls in dresses, boys in shirts.",
        body_sm:
          "Tama'ita'i: puletasi po o se ofu umi fa'aaloalo; pulou le ulu mo le lotu. Alii: ie faitaga ma se ofu pa'epa'e ma le fusi ua, po o se suti atoatoa. Tamaiti: mama ma lā'ei lelei; tama'ita'i i ofu, tama i ofutino.",
      },
      {
        step: 2,
        title_en: 'Funeral',
        title_sm: 'Maliu',
        body_en: 'Black or very dark colours. Conservative. No bright prints. Shoulders covered.',
        body_sm: "Lanu uliuli pe pogisa. Fa'aaloalo. Aua ni lanu fiafia. Pulou tau'au.",
      },
      {
        step: 3,
        title_en: 'Wedding / saofa\'i',
        title_sm: 'Fa\'aipoipoga / saofa\'i',
        body_en:
          "Formal puletasi or formal suit. White or coordinated palette as agreed by the aiga. Ie faitaga is appropriate for matai and for many guests.",
        body_sm:
          "Puletasi aloa'ia po o se suti aloa'ia. Pa'epa'e po o ni lanu ua malilie i ai le aiga. E talafeagai le ie faitaga mo matai ma le tele o malo.",
      },
      {
        step: 4,
        title_en: 'Casual family / village context',
        title_sm: 'Aiga / nu\'u i aso masani',
        body_en: 'Lavalava and t-shirt, modest. Still avoid swimwear or shorts in village centres.',
        body_sm: "Lavalava ma se mitiafu, fa'aaloalo. Aua lava ofu ta'ele po o ofu pupu'u i le ogatotonu o le nu'u.",
      },
    ],
    review: d,
  },
];

export const articleById = Object.fromEntries(articles.map((a) => [a.id, a]));

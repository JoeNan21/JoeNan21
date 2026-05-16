export interface WizardOption {
  id: string;
  label_en: string;
  label_sm: string;
}

export interface WizardQuestion {
  id: string;
  label_en: string;
  label_sm: string;
}

export interface WizardAnswer {
  event: string;
  role: string;
  question: string;
  title_en: string;
  title_sm: string;
  guidance_en: string[];
  guidance_sm: string[];
  link?: { kind: 'ceremony' | 'article'; id: string };
}

export const events: WizardOption[] = [
  { id: 'wedding', label_en: 'Wedding', label_sm: `Fa'aipoipoga` },
  { id: 'funeral', label_en: 'Funeral / ifoga', label_sm: 'Maliu / Ifoga' },
  { id: 'saofai', label_en: `Title bestowal (saofa'i)`, label_sm: `Saofa'i` },
  { id: 'white-sunday', label_en: 'White Sunday', label_sm: 'Lotu a Tamaiti' },
  { id: 'church-dedication', label_en: 'Church dedication', label_sm: `Fa'apa'iaga falesa` },
  { id: 'birthday-first', label_en: 'First birthday', label_sm: 'Aso fanau muamua' },
  { id: 'graduation', label_en: 'Graduation', label_sm: `Fa'au'uga` },
];

export const roles: WizardOption[] = [
  { id: 'guest', label_en: 'Guest', label_sm: 'Malo' },
  { id: 'family-hosting', label_en: 'Family of the hosting aiga', label_sm: 'Aiga e talimalo' },
  { id: 'family-visiting', label_en: 'Family of a visiting aiga', label_sm: 'Aiga asiasi' },
  { id: 'matai', label_en: 'Matai', label_sm: 'Matai' },
  { id: 'tulafale', label_en: 'Tulafale', label_sm: 'Tulafale' },
];

export const questions: WizardQuestion[] = [
  { id: 'what-to-bring', label_en: 'What do I bring?', label_sm: 'O le ā e te aumai?' },
  { id: 'what-to-wear', label_en: 'What do I wear?', label_sm: 'O le ā e te ofuina?' },
  { id: 'when-to-arrive', label_en: 'When do I arrive?', label_sm: `O afea e te taunu'u ai?` },
  { id: 'how-to-greet', label_en: 'How do I greet matai?', label_sm: `O le fa'afeiloa'i matai?` },
  { id: 'where-to-sit', label_en: 'Where do I sit?', label_sm: 'O fea e te nofo ai?' },
  { id: 'how-to-give', label_en: 'How do I give my contribution?', label_sm: `Tu'uina atu o le fesoasoani?` },
  { id: 'cant-contribute', label_en: 'I cannot contribute the full amount', label_sm: `E le mafai ona ou fa'ataunu'u` },
];

export const answers: WizardAnswer[] = [
  {
    event: 'wedding',
    role: 'guest',
    question: 'what-to-bring',
    title_en: 'Wedding — Guest — What to bring',
    title_sm: `Fa'aipoipoga — Malo — Mea e aumai`,
    guidance_en: [
      `A cash gift in an envelope marked clearly with your name. Even a modest amount is welcome — what matters is that you are present and contributing.`,
      `If you are close to either family, ask if they are collecting 'ie toga; if so, you may add one.`,
      `Do not bring elaborate wrapped gifts (toasters, blenders). Cash and 'ie toga are the cultural norm.`,
    ],
    guidance_sm: [
      `O se meaalofa tupe i totonu o se teutusi ma lou igoa. E lava lava se aofa'i itiiti — o le mea taua o lou auai ma le fesoasoani.`,
      `Pe afai e te vavalalata ma se tasi o aiga, fesili pe o lo'o aoaoina 'ie tōga; pe afai e ioe, e mafai ona e fa'aopoopo se tasi.`,
      `Aua ni meaalofa tetele ua afifia (toaster, blender). O le tupe ma le 'ie tōga le mea masani o le aganu'u.`,
    ],
    link: { kind: 'ceremony', id: 'wedding' },
  },
  {
    event: 'wedding',
    role: 'family-hosting',
    question: 'what-to-bring',
    title_en: 'Wedding — Hosting family — What to prepare',
    title_sm: `Fa'aipoipoga — Aiga talimalo — Mea e saunia`,
    guidance_en: [
      `Confer with your matai/sa'o on the aiga's collective contribution.`,
      `'Ie toga: many — for presentation to the other family and for distribution to attending matai.`,
      `Substantial food: umu, additional cooked dishes, drinks.`,
      `Cash for sua, taupou ula gifts, and the wider exchange.`,
      `Take an inventory beforehand — quantity will be noted.`,
    ],
    guidance_sm: [
      `Fesili i lou matai/sa'o e uiga i le fesoasoani a le aiga atoa.`,
      `'Ie tōga: e tele — mo le isi aiga ma mo matai uma o le aoao.`,
      `Mea'ai e tele: umu, mea'ai fa'aopoopo, mea inu.`,
      `Tupe mo le sua, ula a le taupou, ma le tu'ufa'atasiga atoa.`,
      `Fai se lisi a'o le'i o'o le aso — e fa'amauina.`,
    ],
    link: { kind: 'ceremony', id: 'wedding' },
  },
  {
    event: 'wedding',
    role: 'guest',
    question: 'what-to-wear',
    title_en: 'Wedding — Guest — What to wear',
    title_sm: `Fa'aipoipoga — Malo — La'ei`,
    guidance_en: [
      `Women: puletasi or formal dress. Shoulders covered. Modest length. Head covered for the church service.`,
      `Men: ie faitaga and white shirt with tie, or full suit.`,
      `Avoid bright tourist prints, very short hems, or anything beachy.`,
    ],
    guidance_sm: [
      `Tama'ita'i: puletasi po o se ofu aloa'ia. Pulou tau'au. Ofu e talafeagai. Pulou le ulu mo le lotu.`,
      `Alii: ie faitaga ma se ofu pa'epa'e ma le fusi ua, po o se suti atoatoa.`,
      `Aua le ofuina o mea fa'aturisi, ofu pupu'u, po o mea o le matafaga.`,
    ],
    link: { kind: 'ceremony', id: 'wedding' },
  },
  {
    event: 'funeral',
    role: 'family-visiting',
    question: 'what-to-bring',
    title_en: 'Funeral — Visiting family — What to bring',
    title_sm: 'Maliu — Aiga asiasi — Mea e aumai',
    guidance_en: [
      `Confer with your matai before going. The aiga's contribution will usually be coordinated together.`,
      `'Ie toga: the heaviest contribution. The number is decided by your matai.`,
      `Cash in named envelopes per branch of the aiga.`,
      `Food contribution if requested by the bereaved aiga.`,
      `Plan to stay for the lauga, the meal, and the burial — not just one of these.`,
    ],
    guidance_sm: [
      `Fesili i lou matai a'o le'i alu. E masani lava ona soalaupule fesoasoani a le aiga atoa.`,
      `'Ie tōga: o le fesoasoani sili ona mamafa. E filifili e lou matai le aofa'i.`,
      `Tupe i teutusi ua i ai igoa o lala ta'itasi o le aiga.`,
      `Mea'ai pe afai ua mana'omia e le aiga ua tigaina.`,
      `Fuafua e te nofo mo le lauga, le taumafataga, ma le falelauasiga — ae le na o le tasi.`,
    ],
    link: { kind: 'ceremony', id: 'funeral' },
  },
  {
    event: 'funeral',
    role: 'guest',
    question: 'what-to-bring',
    title_en: 'Funeral — Guest — What to bring',
    title_sm: 'Maliu — Malo — Mea e aumai',
    guidance_en: [
      `A cash contribution in a named envelope. This is the minimum — every visitor is expected to contribute.`,
      `If you are close to the family, ask if you should bring 'ie toga or food. Do not assume — ask.`,
      `Black or very dark clothing. No exceptions.`,
    ],
    guidance_sm: [
      `Se fesoasoani tupe i se teutusi ma lou igoa. O le mea sili ona pito i lalo — e fa'amoemoeina malo uma e fesoasoani.`,
      `Pe afai e te vavalalata ma le aiga, fesili pe e aumai 'ie tōga po o mea'ai. Aua ne'i manatu na'o oe — fesili.`,
      `La'ei uliuli pe pogisa lava. E leai se tuusaunoaga.`,
    ],
    link: { kind: 'ceremony', id: 'funeral' },
  },
  {
    event: 'funeral',
    role: 'guest',
    question: 'how-to-greet',
    title_en: 'Funeral — Greeting the bereaved',
    title_sm: `Maliu — Fa'afeiloa'i le aiga ua tigaina`,
    guidance_en: [
      `Approach softly. A handshake or quiet embrace is appropriate. Lower your voice.`,
      `Use mālō le onosa'i (well borne) or alofa atu (love to you).`,
      `Do not ask how the deceased died. Do not stay too long in the line if many are waiting.`,
    ],
    guidance_sm: [
      `Fa'alatalata ma le filemu. E talafeagai se lulu lima po o se fusi pu'upu'u. Tautala lemu.`,
      `Fa'aaogā mālō le onosa'i po o alofa atu.`,
      `Aua e te fesili pe na maliu fa'apefea. Aua le tu umi i le laina pe afai e tele e fa'atali.`,
    ],
    link: { kind: 'ceremony', id: 'funeral' },
  },
  {
    event: 'saofai',
    role: 'family-hosting',
    question: 'what-to-bring',
    title_en: `Saofa'i — Bestowing aiga — What to prepare`,
    title_sm: `Saofa'i — Aiga e tu'uina atu — Mea e saunia`,
    guidance_en: [
      `'Ie toga in significant number — this is a major fa'alavelave.`,
      `Cash for the village fono (consult your sa'o on the amount).`,
      `'Ava root.`,
      `Pigs, taro, and an umu sufficient to feed the village fono.`,
      `Formal la'ei for the candidate and all aiga members at the saofa'i.`,
    ],
    guidance_sm: [
      `'Ie tōga e tele — o se fa'alavelave mamafa.`,
      `Tupe mo le fono a le nu'u (fesili i lou sa'o mo le aofa'i).`,
      `A'a o le 'ava.`,
      `Pua'a, talo, ma se umu ua lava e fafaga ai le fono a le nu'u.`,
      `La'ei aloa'ia mo le sui ma le aiga atoa i le saofa'i.`,
    ],
    link: { kind: 'ceremony', id: 'saofai' },
  },
  {
    event: 'white-sunday',
    role: 'family-hosting',
    question: 'what-to-bring',
    title_en: 'White Sunday — What to prepare',
    title_sm: 'Lotu a Tamaiti — Mea e saunia',
    guidance_en: [
      `White la'ei for every child of the aiga.`,
      `A memorised verse or song per child — even the youngest.`,
      `A larger-than-usual Sunday lunch. The children are served first.`,
      `No gifts to adults — this day belongs to the children.`,
    ],
    guidance_sm: [
      `La'ei pa'epa'e mo tamaiti uma o le aiga.`,
      `Se tauloto po o se pese ua sauni — e o'o lava i e laiti.`,
      `Se to'ona'i e tele atu nai lo le masani. E mua'i tausi tamaiti.`,
      `Aua ni meaalofa i tagata matutua — o le aso e mo tamaiti.`,
    ],
    link: { kind: 'ceremony', id: 'white-sunday' },
  },
  {
    event: '*',
    role: '*',
    question: 'cant-contribute',
    title_en: 'I cannot contribute the full amount',
    title_sm: `E le mafai ona ou fa'ataunu'u atoatoa`,
    guidance_en: [
      `Communicate as early as possible. Speak to your matai, your sa'o, or — if you are external — directly to the host aiga's tulafale.`,
      `Use the word fa'atoesega (apology). State plainly: 'O lo'u fa'atoesega' — this is my apology.`,
      `Send what you can with respect. A small contribution well-named and accompanied by an explanation is honoured.`,
      `Do not send nothing without word. Silence is the failure; partial contribution with communication is not.`,
    ],
    guidance_sm: [
      `Talanoa vave. Fesili i lou matai, lou sa'o, po o — pe afai e te i fafo — fa'asa'o atu i le tulafale o le aiga e talimalo.`,
      `Fa'aaogā le upu fa'atoesega. Ta'u manino atu: 'O lo'u fa'atoesega.'`,
      `Tu'uina atu le mea e mafai ma le fa'aaloalo. O se fesoasoani itiiti ma le igoa ma le fa'amatalaga e fa'aaloalogia.`,
      `Aua le auina atu se mea aunoa ma le tala. O le filemu — o le sese; o le fesoasoani itiiti ma le talanoaga — e le sese.`,
    ],
    link: { kind: 'article', id: 'faalavelave-overview' },
  },
  {
    event: '*',
    role: 'guest',
    question: 'where-to-sit',
    title_en: 'Where do I sit as a guest?',
    title_sm: 'O fea e nofo ai se malo?',
    guidance_en: [
      `Not in the matai row — that is the front. Behind the matai of your aiga, or in the guest seating indicated by the host tulafale.`,
      `Wait to be shown; do not pick a seat alone.`,
      `If sitting on the floor in a fale samoa, keep legs crossed or tucked under — never pointed at the matai.`,
    ],
    guidance_sm: [
      `Aua i le laina o matai — o luma lena. I tua o matai o lou aiga, po o le nofoaga o malo ua fa'asino e le tulafale.`,
      `Fa'atali se'i fa'asino atu; aua na'o oe e fa'aiu.`,
      `Pe afai o le a nofo i lalo i se fale samoa, fa'atautau vae i lalo — aua ne'i fa'asaga vae i matai.`,
    ],
  },
];

export function findAnswer(event: string, role: string, question: string): WizardAnswer | undefined {
  return (
    answers.find((a) => a.event === event && a.role === role && a.question === question) ||
    answers.find((a) => (a.event === event || a.event === '*') && a.role === role && a.question === question) ||
    answers.find((a) => a.event === event && (a.role === role || a.role === '*') && a.question === question) ||
    answers.find((a) => (a.event === '*' || a.event === event) && (a.role === '*' || a.role === role) && a.question === question)
  );
}

export function getBrowserLocale(): string {
    let lang;
    if (navigator.languages && navigator.languages.length) {
        lang = navigator.languages;
    }
    lang = navigator.language;
    return "da-DK";
}
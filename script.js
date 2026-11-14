const categories = {
  showers: ["SHOWER SYSTEMS", "الشاورات", "أنظمة شاور ذكية بتشطيبات مختلفة، منها الكروم والأسود المطفي والذهبي الشامبانيا.", "من موديلات المجموعة: Milano، Ferrari، وNaqaa Plus.", "الشاورات"],
  mixers: ["JAVA MIX 2027", "أطقم خلاطات JAVA MIX", "تشكيلة أطقم خلاطات JAVA MIX.", "", "أطقم خلاطات JAVA MIX"],
  luxuryMixers: ["TREND OF MIXER", "خلاطات لاكشوري 2027", "تشكيلة خلاطات لاكشوري لعام 2027.", "", "خلاطات لاكشوري 2027"],
  vanities: ["VANITIES", "المغاسل والكبائن", "مغاسل مع كبائن معلّقة من PVC Foam، بخيارات متعددة من المقاسات والألوان.", "من موديلات المجموعة: GOLF وOMEGA وL700H.", "المغاسل والكبائن"],
  toilets: ["TOILETS", "التواليتات", "تواليتات معلّقة ولوازم خزانات الدفن، بما فيها كبسات التشغيل.", "حدّد الموديل أو ابعث صورة القطعة المطلوبة للاستفسار عن التوافق والتوفّر.", "التواليتات"],
  accessories: ["BATHROOM ACCESSORIES", "الإكسسوارات", "حاملات مناشف، موزّعات صابون، شطّافات، مصارف أرضية ومرايا بإضاءة لمس.", "تختلف المقاسات والتشطيبات حسب القطعة.", "الإكسسوارات"],
  encastre: ["ENCASTRE", "دفن Encastre", "تجهيزات دفن للحمّام.", "", "دفن Encastre"]
};
const selectors = [...document.querySelectorAll("[data-category]")];
const fields = ["category-en", "category-title", "category-description", "category-examples"].map(id => document.getElementById(id));
const contact = document.getElementById("category-contact");
const catalogLinks = document.querySelectorAll("[data-catalog-for]");

function selectCategory(button) {
  const category = categories[button.dataset.category];
  catalogLinks.forEach(links => {
    links.hidden = links.dataset.catalogFor !== button.dataset.category;
  });
  selectors.forEach(selector => selector.setAttribute("aria-pressed", String(selector === button)));
  fields.forEach((field, index) => { field.textContent = category[index]; });
  contact.firstChild.nodeValue = `استفسر عن ${category[4]} `;
  contact.href = `https://wa.me/963944881127?text=${encodeURIComponent(`مرحباً، حابب استفسر عن ${category[4]} المتوفّرة عندكم.`)}`;
}
selectors.forEach(button => button.addEventListener("click", () => selectCategory(button)));
selectCategory(selectors[0]);

document.querySelectorAll(".copy-whatsapp").forEach(button => {
  button.addEventListener("click", async () => {
    const number = button.parentElement.querySelector("bdi");
    const status = button.parentElement.querySelector("[role=status]");
    try {
      await navigator.clipboard.writeText(number.textContent);
      status.textContent = "تم نسخ الرقم";
    } catch {
      status.textContent = "اضغط مطوّلاً على الرقم لنسخه";
    }
  });
});

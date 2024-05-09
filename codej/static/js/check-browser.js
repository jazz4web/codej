function checkBrowser() {
  let brand = '';
  try {
    for (let i of navigator.userAgentData.brands) {
      brand += i.brand;
      brand += i.version;
    }
  } catch (TypeError) {
    // pass;
  }
  let br = navigator.userAgent + brand + navigator.language +
           new Date().getTimezoneOffset() +
           screen.height + screen.width + screen.colorDepth;
  return SparkMD5.hash(br);
}

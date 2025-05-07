function analyze() {
  const fileInput = document.getElementById('upload');
  const file = fileInput.files[0];
  if (!file) return alert("Выберите файл");

  const formData = new FormData();
  formData.append("file", file);

  fetch("https://teplo.onrender.com/analyze/", {
    method: "POST",
    body: formData,
  })
  .then((res) => {
    if (res.ok) return res.blob();
    return res.json().then(err => { throw new Error(err.detail || "Ошибка сервера"); });
  })
  .then((blob) => {
    const url = window.URL.createObjectURL(blob);
    const link = document.getElementById("download");
    link.href = url;
    link.download = "report.pdf";
    link.style.display = "inline-block";
  })
  .catch((err) => {
    document.getElementById("result").innerText = "Ошибка: " + err.message;
  });
}

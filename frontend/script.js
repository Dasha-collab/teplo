function analyze() {
  const fileInput = document.getElementById('upload');
  const file = fileInput.files[0];
  
  if (!file) {
    alert("Пожалуйста, выберите файл изображения (JPEG/PNG)");
    return;
  }

  // Проверка типа файла
  if (!file.type.match('image.*')) {
    alert("Только изображения (JPEG/PNG) поддерживаются");
    return;
  }

  const resultDiv = document.getElementById("result");
  const downloadLink = document.getElementById("download");
  
  // Очистка предыдущих результатов
  resultDiv.innerText = "";
  downloadLink.style.display = "none";

  // Показываем индикатор загрузки
  resultDiv.innerText = "Идёт анализ...";

  const formData = new FormData();
  formData.append("file", file);

  fetch("https://teplo.onrender.com/analyze/", {
    method: "POST",
    body: formData,
  })
  .then(async (response) => {
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || "Ошибка сервера");
    }
    return response.blob();
  })
  .then((blob) => {
    const url = window.URL.createObjectURL(blob);
    downloadLink.href = url;
    downloadLink.download = "teplo_report.pdf";
    downloadLink.style.display = "inline-block";
    resultDiv.innerText = "Анализ завершён!";
  })
  .catch((error) => {
    console.error("Ошибка:", error);
    resultDiv.innerText = "Ошибка: " + error.message;
  });
}

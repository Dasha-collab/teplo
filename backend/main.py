<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Teplo PP - анализ упаковки</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <div class="container">
    <h1>Teplo PP - анализ упаковки</h1>
    <p>Загрузите фото упаковки для анализа зоны восприятия</p>
    
    <div id="upload-area">
      <p>Перетащите изображение сюда или кликните для выбора</p>
      <input type="file" id="upload" accept="image/*" style="display:none">
      <img id="preview" alt="Предпросмотр изображения">
    </div>
    
    <button onclick="analyze()">Анализировать</button>
    <div id="result"></div>
    <a id="download" class="download-btn" style="display:none">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
        <polyline points="7 10 12 15 17 10"></polyline>
        <line x1="12" y1="15" x2="12" y2="3"></line>
      </svg>
      Скачать отчёт PDF
    </a>
  </div>

  <script>
    // Обработка выбора файла с предпросмотром
    document.getElementById('upload').addEventListener('change', function(e) {
      const file = e.target.files[0];
      if (!file) return;
      
      const preview = document.getElementById('preview');
      const reader = new FileReader();
      
      reader.onload = function(e) {
        preview.src = e.target.result;
        preview.style.display = 'block';
        document.getElementById('result').innerText = "";
        document.getElementById('download').style.display = "none";
      }
      
      reader.readAsDataURL(file);
    });

    // Обработка клика по области загрузки
    document.getElementById('upload-area').addEventListener('click', function() {
      document.getElementById('upload').click();
    });

    // Функция анализа
    function analyze() {
      const fileInput = document.getElementById('upload');
      const file = fileInput.files[0];
      
      if (!file) {
        alert("Пожалуйста, выберите файл изображения (JPEG/PNG)");
        return;
      }

      const resultDiv = document.getElementById('result');
      const downloadLink = document.getElementById('download');
      
      resultDiv.innerText = "";
      downloadLink.style.display = "none";
      resultDiv.innerText = "Идёт анализ...";

      const formData = new FormData();
      formData.append('file', file);

      fetch('https://teplo.onrender.com/analyze/', {
        method: 'POST',
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
        downloadLink.download = 'teplo_analysis.pdf';
        downloadLink.style.display = 'inline-flex';
        resultDiv.innerText = 'Анализ завершён!';
      })
      .catch((error) => {
        console.error('Ошибка:', error);
        resultDiv.innerText = 'Ошибка: ' + (error.message || 'Произошла неизвестная ошибка');
      });
    }
  </script>
</body>
</html>

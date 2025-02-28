<script setup>
import { ref, onMounted } from 'vue';
import { TheChessboard } from "vue3-chessboard";
import "vue3-chessboard/style.css";
// import axios from 'axios';
const isGameStarted = ref(false); // Переменная для отслеживания состояния игры
const selectedDifficulty = ref('1'); // Переменная для хранения выбранного уровня сложности


function startGame() {
  isGameStarted.value = true; // Изменяем состояние на "игра начата"
}

let boardAPI;
const boardConfig = {
  coordinates: true,
};

const moveHistory = ref([]); // Переменная для хранения истории ходов
const currentColor = ref('w');

function recordMove(move) {
  moveHistory.value.push(move); // Добавляем ход в историю
  currentColor.value = move.color; // Обновляем текущий цвет игрока
  // sendMoveToGigaChat(move); // Отправляем запрос в GigaChat

}

function resetGame() {
  boardAPI?.resetBoard();
  moveHistory.value = [];
  currentColor.value = 'w';
}

onMounted(() => {
  const script = document.createElement('script');
  script.src = "https://telegram.org/js/telegram-web-app.js";
  script.async = true;
  document.body.appendChild(script);
});


// async function sendMoveToGigaChat(move) {
//   const fen = `${move.after}`; // Замените на актуальный FEN
//   console.log("move.after = " + move.after)
//   const moveHistoryString = moveHistory.value.map(m => m.to).join(', '); // Преобразуем историю ходов в строку

//   const prompt = `You are playing ${currentColor.value === 'w' ? 'white' : 'black'} and it is your turn.\n\n` +
//                  `This is the current state of the game use this to work out where the pieces are on the board:\n\n` +
//                  `FEN for ${currentColor.value === 'w' ? 'white' : 'black'}: ${fen}\n` +
//                  `Move History: ${moveHistoryString}\n\n` +
//                  `Output the best move in SAN format to follow this position. Use the following single blob of JSON. Do not include any other information.\n\n` +
//                  `{\n  "san": "The move in SAN format",\n  "reason": "Why this is a good move"\n}`;

//   try {
//     const response = await axios.post('https://gigachat.devices.sberbank.ru/api/v1/chat/completions', {
//       model: "GigaChat-Pro", // Выберите нужную модель
//       messages: [
//         {
//           role: "user",
//           content: prompt
//         }
//       ],
//       n: 1,
//       stream: false,
//       max_tokens: 512,
//       repetition_penalty: 1,
//       update_interval: 0
//     }, {
//       headers: {
//         'Content-Type': 'application/json',
//         'Authorization': 'Bearer OTAyZjAzNTctMTVhOC00M2YzLTkyMmQtNDY0MzRiMGNhMzQ2OjkxNzlmNGExLTE5YzgtNDUwZS04ZjVhLWE3NDEwNjVlZTlkNQ==' // Замените на ваш токен доступа
//       }
//     });

//     const bestMove = response.data.choices[0].message.content; // Извлекаем лучший ход из ответа
//     console.log(bestMove); // Выводим лучший ход в консоль
//     // Здесь вы можете добавить логику для отображения лучшего хода пользователю
//   } catch (error) {
//     console.error("Ошибка при отправке запроса в GigaChat:", error);
//   }
// }


// let tg = window.Telegram.WebApp;
// let game = document.getElementById("game");

// game.addEventListener("click", () => {
//   document.getElementById("main").style.display == "none";
//   document.getElementById("menu").style.display == "block";
// });


</script>
<!-- // name: 'MyComponent',
  // mounted() {
  //   const script = document.createElement('script');
  //   script.src = "https://telegram.org/js/telegram-web-app.js";
  //   script.async = true;
  //   document.body.appendChild(script);
  // },
   -->


<template title>
  <div id="main" v-show="isGameStarted">
    <h1>MireaChess</h1>
    <div id="move-history">
      <div id="selectedOptions">
        <p>Выбранный цвет: {{ selectedColor === 'w' ? 'белые' : 'чёрные' }}</p>
        <p>Уровень сложности: {{ selectedDifficulty }}</p>
      </div>
      <span v-if="moveHistory.length === 0">Сделайте первый ход!</span>
      <span v-else>
        <span v-for="(move, index) in moveHistory" :key="index">{{ index + 1 }}. {{ move.to }}<span v-if="index < moveHistory.length - 1">, </span></span>
      </span>
    </div>
    <div id="board">
      <TheChessboard 
      @move="recordMove"
      :board-config="boardConfig"
      @board-created="(api) => (boardAPI = api)"
       /> <!-- Слушаем событие хода -->
    </div>
      <div id="status">
        <div v-if="moveHistory.length === 0">Ходят белые</div>
        <div v-else>Ходят {{ currentColor === 'w' ? 'чёрные' : 'белые' }}</div>
      </div>
      <div className="menu">
      <button @click="boardAPI?.toggleOrientation()">Повернуть доску</button>
      <button @click="resetGame()">Начать сначала</button>
      <button @click="boardAPI?.undoLastMove()">Ход назад</button>
      
    </div>
  </div>
    
<!-- ЗАПРОС В ГПТ : move.after -->

    

  <!-- ТУТ БУДЕТ МЕНЮ ВЫБОРА СЛОЖНОСТИ БОТА И ВСЯКИЕ НАСТРОЙКИ -->
  <div id="start" v-show="!isGameStarted">
    <h2>Добро пожаловать!</h2>
    <h4>За кого играете: 
      <select  v-model="selectedColor">
        <option value="w">белые</option>
        <option value="b">чёрные</option>
      </select>
    </h4>
    <h4>Сложность бота:
      <select v-model="selectedDifficulty">
        <option value="1">400 elo</option>
        <option value="2">1200 elo</option>
        <option value="3">2500 elo</option>
      </select>
    </h4>
    
    <button @click="startGame" id="game">Играть</button>
  </div>
</template>

<style>
#main {
  border: 2px solid red;
}

#start {
  border: 2px solid red;
  padding: 10px;
  margin: 10px;

}

#start select {
  width:80px;
  height: 50px;
  
}

#board {
  margin: auto;
  border: 2px solid black;
  width: 700px;
  height: 700px;
}

.menu {
  display: grid;
  grid-template-columns: 33% 33% 33%;
  margin: auto;
  width: 400px;
  height: auto;
  border: 2px solid black;
  font-size: 12px;
}

.menu button {
  margin: 10px;
  padding: 5px;
}

.menu select {
  margin: 10px;
  padding: 5px;
}

#move-history {
  background-color: rgb(83, 83, 83);
  width: 704px;
  margin: 20px;
  margin-bottom: 0;
}

#game {
  border: 0;
  border-radius: 5px;
  width: 100px;
  height: 50px;
  text-align: center;
}
</style>
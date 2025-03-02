<script setup>
import { ref, onMounted } from "vue";
import { TheChessboard } from "vue3-chessboard";
import "vue3-chessboard/style.css";
import axios from "axios";
const isGameStarted = ref(false); // Переменная для отслеживания состояния игры
const selectedDifficulty = ref("1"); // Переменная для хранения выбранного уровня сложности

function startGame() {
  isGameStarted.value = true; // Изменяем состояние на "игра начата"
}

let boardAPI;
const boardConfig = {
  coordinates: true,
};

const moveHistory = ref([]); // Переменная для хранения истории ходов
const currentColor = ref("w");

function recordMove(move) {
  moveHistory.value.push(move); // Добавляем ход в историю
  currentColor.value = move.color; // Обновляем текущий цвет игрока
  // +++++++++++++++++++++

  sendMoveToGigaChat(move); // Отправляем запрос в GigaChat
}

function resetGame() {
  boardAPI?.resetBoard();
  moveHistory.value = [];
  currentColor.value = "w";
}

onMounted(() => {
  const script = document.createElement("script");
  script.src = "https://telegram.org/js/telegram-web-app.js";
  script.async = true;
  document.body.appendChild(script);
});

async function sendMoveToGigaChat(move) {
  const fen = `${move.after}`;
  console.log(move); // Замените на актуальный FEN
  console.log("move.after = " + move.after);
  const moveHistoryJson = boardAPI?.getHistory(true);
  let moveHistoryString = "";
  for (let index = 0; index < moveHistoryJson.length; index++) {
    const cur = index + 1;
    moveHistoryString +=
      cur +
      ". " +
      moveHistoryJson[index].from +
      moveHistoryJson[index].to +
      " ";
  }
  console.log(moveHistoryString); // Преобразуем историю ходов в строку

  const prompt =
    `Ты играешь в шахматы. Сейчас ты ходишь за ${
      currentColor.value === "b" ? "белых" : "черных"
    }\n\n` +
    // `Вот текущее положение доски в формате FEN: ` +
    // `${fen}\n` +
    `История ходов: ${JSON.stringify(moveHistoryString)}\n\n` +
    `Из этих данных выдай мне ход строго в формате LAN. То есть код ячейки откуда ходишь и куда. Возвращать просто ячейку куда ты сходишь нельзя, обязательно должна быть ячейка откуда ты походил. Из этого верни мне JSON. Не вставляй другую информацию. Не повторяй ходы, которые уже были сделаны ЭТО ОЧЕНЬ ВАЖНО!!! Сравнивай ходы из истории ходов, которую я тебе дал. Доска не переворачивается, то есть король черных находится на 8 строке\n\n` +
    `{\n  "lan": "Ход строго в формате LAN",\n  "reason": "Почему этот ход хорош"\n}`;

  try {
    const response = await axios.post(
      "http://localhost:8000/api/chat",
      {
        message: prompt,
        user_id: "4f7b26d4-2fea-486e-a6fd-375881330ba2",
      },
      {
        headers: {
          "Content-Type": "application/json",
          Authorization:
            "Bearer OTAyZjAzNTctMTVhOC00M2YzLTkyMmQtNDY0MzRiMGNhMzQ2OjkxNzlmNGExLTE5YzgtNDUwZS04ZjVhLWE3NDEwNjVlZTlkNQ==", // Замените на ваш токен доступа
        },
      }
    );

    console.log(response.data);

    const responseData = JSON.parse(response.data.response);
    console.log(prompt);
    console.log(responseData);
    const bestMove = responseData.lan;
    boardAPI?.move(bestMove);
    console.log(bestMove); // Выводим лучший ход в консоль
    // Здесь вы можете добавить логику для отображения лучшего хода пользователю
  } catch (error) {
    console.error("Ошибка при отправке запроса в GigaChat:", error);
  }
}

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
        <p>Выбранный цвет: {{ selectedColor === "w" ? "белые" : "чёрные" }}</p>
        <p>Уровень сложности: {{ selectedDifficulty }}</p>
      </div>
      <span v-if="moveHistory.length === 0">Сделайте первый ход!</span>
      <span v-else>
        <span v-for="(move, index) in moveHistory" :key="index"
          >{{ index + 1 }}. {{ move.to
          }}<span v-if="index < moveHistory.length - 1">, </span></span
        >
      </span>
    </div>
    <div id="board">
      <TheChessboard
        @move="recordMove"
        :board-config="boardConfig"
        @board-created="(api) => (boardAPI = api)"
      />
      <!-- Слушаем событие хода -->
    </div>
    <div id="status">
      <div v-if="moveHistory.length === 0">Ходят белые</div>
      <div v-else>Ходят {{ currentColor === "w" ? "чёрные" : "белые" }}</div>
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
    <h4>
      За кого играете:
      <select v-model="selectedColor">
        <option value="w">белые</option>
        <option value="b">чёрные</option>
      </select>
    </h4>
    <h4>
      Сложность бота:
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
  width: 80px;
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

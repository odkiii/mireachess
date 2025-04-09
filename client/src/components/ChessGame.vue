<script setup>
import { ref, onMounted, watch, nextTick } from "vue";
import { TheChessboard } from "vue3-chessboard";
import "vue3-chessboard/style.css";
import axios from "axios";
import "./styles.css";  

const isGameStarted = ref(false);
const selectedDifficulty = ref("1");
const selectedColor = ref("w");
const moveHistory = ref([]);
const movesContainer = ref(null); // Реф для контейнера ходов
let boardAPI;
const isModalVisible = ref(false);
const isDrawModalVisible = ref(false);
const isResignModalVisible = ref(false);
const winner = ref('');
const boardConfigForWhite = {
  coordinates: true,
  orientation: "white",
};
const API_URL = 'https://mireachessapi.cloudpub.ru/';



// Улучшенная функция прокрутки
const scrollToEnd = () => {
  nextTick(() => {
    if (!movesContainer.value) return;
    
    // Двойная страховка - два способа прокрутки
    movesContainer.value.scrollTo({
      left: movesContainer.value.scrollWidth,
      behavior: 'smooth'
    });
    
    // На случай если smooth не сработает
    setTimeout(() => {
      movesContainer.value.scrollLeft = movesContainer.value.scrollWidth;
    }, 50);
  });
};

// Следим за изменениями истории ходов
watch(moveHistory, scrollToEnd, { deep: true });

// Прокрутка колесиком мыши
const handleWheel = (e) => {
  if (movesContainer.value) {
    movesContainer.value.scrollLeft += e.deltaY;
    // Отменяем стандартное поведение страницы
    e.preventDefault();
  }
};

//Сдаться
function confirmResign() {
  isResignModalVisible.value = true; // Показываем модальное окно подтверждения
  handleCheckmate(winner.value); // Передаем значение winner
  isResignModalVisible.value = false; // Скрываем модальное окно подтверждения
}

//Мат
function handleCheckmate(isMated) {
  const winnerColor = isMated === 'w' ? 'Чёрные' : 'Белые';
  winner.value = winnerColor;
  isModalVisible.value = true;
}

//Ничья
function handleDraw() {
  isDrawModalVisible.value = true; // Показываем модальное окно ничьей
}

async function startGame() {
  let diff = 1;
  if (selectedDifficulty.value === "2") {
    diff = 10;
  } else if (selectedDifficulty.value === "3") {
    diff = 20;
  }
  console.log(diff);
  try {
    const response = await axios.post("https://mireachessapi.cloudpub.ru/api/start", {
      diff: diff,
    });
    console.log(response.data);
  } catch (error) {
    console.error("Ошибка при отправке запроса: ", error);
  }
  isGameStarted.value = true;

  if (selectedColor.value === "b") {
    boardAPI?.toggleOrientation();
    sendMove(boardAPI?.getFen());
  }
}

function recordMove() {
  const lastMove = boardAPI?.getLastMove();
  moveHistory.value.push(lastMove.lan);
  console.log(moveHistory);
  if (lastMove.color === selectedColor.value) {
    sendMove(lastMove.after);
  }
  scrollToEnd(); 
}

function resetGame() {
  boardAPI?.resetBoard();
  moveHistory.value = [];
  isModalVisible.value = false; // Скрываем модальное окно при сбросе игры
  isDrawModalVisible.value = false; // Скрываем модальное окно ничьей

}

const telegram_id = ref(null);

onMounted(() => {
  if (window.Telegram?.WebApp?.initDataUnsafe?.user) {
    telegram_id.value = Telegram.WebApp.initDataUnsafe.user.id;
    console.log("Telegram ID установлен:", telegram_id.value);
  } else {
    telegram_id.value = 0;  // Заглушка для локального тестирования
    console.warn("Telegram WebApp не обнаружен. Используется test ID.");
  }
  const script = document.createElement("script");
  script.src = "https://telegram.org/js/telegram-web-app.js";
  script.async = true;
  document.body.appendChild(script);
  // нужная часть или нет ?
});


async function sendMove(fen) {
  console.log("Отправка хода:", fen, "Telegram ID:", telegram_id.value);
  
  try {
    const response = await axios.post("https://mireachessapi.cloudpub.ru/api/move", {
      fen: fen,
      telegram_id: telegram_id.value || 0,  // 0 для тестов, если нет Telegram
    });
    boardAPI?.move(response.data.best_move);
  } catch (error) {
    console.error("Ошибка при отправке хода:", error.response?.data || error.message);
  }
}

async function showBestMove() {
  // Скрываем предыдущие стрелки перед показом новой
  boardAPI?.hideMoves(); 

  // Получаем текущее состояние доски в формате FEN
  const fen = boardAPI?.getFen(); 

  try {
    // Отправляем запрос на сервер для получения лучшего хода
    // const response = await axios.post("http://localhost:8000/api/move", { fen: fen });
    const response = await axios.post("https://mireachessapi.cloudpub.ru/api/move", { fen: fen });
    const bestMove = response.data.best_move;

    if (bestMove) {
      const orig = bestMove.slice(0, 2); // начальная позиция
      const dest = bestMove.slice(2, 4); // конечная позиция
      boardAPI?.drawMove(orig, dest, 'green'); // Рисуем стрелку
    }
  } catch (error) {
    console.error("Ошибка при получении лучшего хода:", error);
  }
}



</script>


<template title>
  <div id="main" v-show="isGameStarted">
    <h1>MireaChess</h1>
    <div id="move-history">
      <div id="selectedOptions">
        <p>Выбранный цвет: {{ selectedColor === "w" ? "белые" : "чёрные" }}</p>
        <p>Уровень сложности: {{ selectedDifficulty }}</p>
      </div>
      <div id="moves" ref="moves" @wheel.prevent="handleWheel">
        <span v-if="moveHistory.length === 0">Сделайте первый ход!</span>
      <span v-else>
        <span v-for="(move, index) in moveHistory" :key="index">{{ index + 1 }}. {{ move }}<span v-if="index < moveHistory.length - 1">, </span></span>
      </span>
    </div>
      
    </div>
    <div id="board">
      <TheChessboard
        @move="recordMove"
        :board-config="boardConfigForWhite"
        @board-created="(api) => (boardAPI = api)"
        @checkmate="handleCheckmate"
        @draw="handleDraw"

      />
      <!-- Слушаем событие хода -->
    </div>
    <div id="status">
      <div v-if="moveHistory.length === 0">Ходят белые</div>
      <div v-else>Ходят {{ selectedColor === "w" ? "чёрные" : "белые" }}</div>
    </div>
    <div className="menu">
      <button @click="boardAPI?.toggleOrientation()">Повернуть доску</button>
      <button @click="resetGame()">Начать сначала</button>
      <button @click="boardAPI?.undoLastMove()">Ход назад</button>
      <button @click="showBestMove">Помочь с ходом</button>  
      <button @click="isResignModalVisible = true">Сдаться</button> 

    </div>

        <!-- Модальное окно для конца игры -->
    <div v-if="isModalVisible" class="modal-overlay">
      <div class="modal">
        <h2>{{ winner }} проиграли</h2>
        <button class="btn-new" @click="resetGame">Начать новую игру</button>
      </div>
    </div>
        <!-- Модальное окно для ничьей -->
    <div v-if="isDrawModalVisible" class="modal-overlay">
      <div class="modal">
        <h2>Ничья!</h2>
        <button class="btn-new" @click="resetGame">Начать новую игру</button>
      </div>
    </div>
    <!-- Модальное окно для подтверждения сдачи -->
    <div v-if="isResignModalVisible" class="modal-overlay">
      <div class="modal">
        <h2>Вы точно хотите сдаться?</h2>
        <button class="btn-resign" @click="confirmResign">Да</button>
        <button class="btn-new" @click="isResignModalVisible = false">Нет</button>
      </div>
    </div>
  </div>
  
  <!-- ТУТ БУДЕТ МЕНЮ ВЫБОРА СЛОЖНОСТИ БОТА И ВСЯКИЕ НАСТРОЙКИ -->
  <div id="start" v-show="!isGameStarted">
    <h2>
      Добро пожаловать!
      <MireaChess :telegram_id="telegram_id" />
    </h2>
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
        <option value="1">Слабый</option>
        <option value="2">Средний</option>
        <option value="3">Сильный</option>
      </select>
    </h4>

    <button @click="startGame" id="game">Играть</button>
  </div>
  
</template>


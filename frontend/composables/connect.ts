import { ref, onMounted } from 'vue';
import LeaderLine from 'leader-line-new';

export default function useConnect() {
  const fixedConnections = ref([]);
  const activeLine = ref(null);

  const initHoverAndClick = () => {
    const boxes = document.querySelectorAll('.box');
    const targetBox = document.getElementById('target-box');

    boxes.forEach((box) => {
      box.addEventListener('mouseenter', () => {
        if (activeLine.value) {
          activeLine.value.remove();
        }
        activeLine.value = new LeaderLine(box, targetBox, {
          color: 'blue',
          startPlug: 'behind',
          endPlug: 'arrow1',
        });
      });

      box.addEventListener('mouseleave', () => {
        if (activeLine.value) {
          activeLine.value.remove();
          activeLine.value = null;
        }
      });

      box.addEventListener('click', () => {
        if (activeLine.value) {
          activeLine.value.setOptions({ color: 'black' });
          fixedConnections.value.push({
            from: box.id,
            to: targetBox.id,
            line: activeLine.value,
          });
          activeLine.value = null;

          targetBox.textContent = box.id;
        }
      });
    });
  };

  onMounted(async () => {
    initHoverAndClick();
  });

  return { fixedConnections };
}

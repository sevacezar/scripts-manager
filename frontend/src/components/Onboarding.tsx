import { useCallback } from 'react';
import Joyride, { CallBackProps, STATUS, Step } from 'react-joyride';
import { useAuth } from '../contexts/AuthContext';

interface OnboardingProps {
  run: boolean;
  onComplete: () => void;
  onSkip: () => void;
}

const Onboarding = ({ run, onComplete }: OnboardingProps) => {
  const { updateOnboardingStatus } = useAuth();

  const steps: Step[] = [
    {
      target: 'body',
      content: (
        <div className="text-left">
          <h3 className="text-lg font-semibold mb-2">Добро пожаловать в Менеджер скриптов!</h3>
          <p className="text-left">Этот сервис позволяет выполнять Python-скрипты удаленно на сервере через HTTP API.</p>
        </div>
      ),
      placement: 'center',
      disableBeacon: true,
    },
    {
      target: 'body',
      content: (
        <div className="text-left">
          <h3 className="text-lg font-semibold mb-2">Зачем это нужно?</h3>
          <p className="text-left mb-2">Сервис особенно полезен, если:</p>
          <ul className="list-disc list-inside space-y-1 text-left">
            <li className="text-left">На вашем рабочем компьютере нет Python</li>
            <li className="text-left">тНавигатор не поддерживает нужные библиотеки</li>
            <li className="text-left">Нужно выполнить сложные вычисления на сервере</li>
          </ul>
          <p className="text-left mt-2">Вы можете загрузить скрипт на сервер и вызывать его удаленно из тНавигатора!</p>
        </div>
      ),
      placement: 'center',
    },
    {
      target: 'body',
      content: (
        <div className="text-left">
          <h3 className="text-lg font-semibold mb-2">Как это работает?</h3>
          <p className="text-left mb-2">Процесс выполнения скрипта:</p>
          <ol className="list-decimal list-inside space-y-2 text-left">
            <li className="text-left">Из тНавигатора отправляется <strong>HTTP запрос</strong> на сервер с данными (словарь)</li>
            <li className="text-left">Сервер вызывает функцию <code className="bg-gray-100 px-1 rounded">main(data: dict)</code> в вашем скрипте, передавая в нее словарь с данными, которые вы отправили в запросе</li>
            <li className="text-left">Скрипт обрабатывает данные и возвращает <strong>словарь</strong></li>
            <li className="text-left">Сервер отправляет результат обратно в тНавигатор</li>
          </ol>
          <div className="bg-gray-50 p-3 rounded text-sm font-mono text-left mt-3">
            <div className="text-left"># В скрипте:</div>
            <div className="text-left">def main(data: dict) -&gt; dict:</div>
            <div className="ml-4 text-left"># Получаем данные из тНавигатора</div>
            <div className="ml-4 text-left">value = data.get("value")</div>
            <div className="ml-4 text-left"># Обрабатываем...</div>
            <div className="ml-4 text-left">return {"{"}"result": value * 2{"}"}</div>
            <div className="text-left mt-2"># Результат вернется в тНавигатор</div>
          </div>
        </div>
      ),
      placement: 'center',
    },
    {
      target: 'body',
      content: (
        <div className="text-left">
          <h3 className="text-lg font-semibold mb-2">Порядок действий</h3>
          <p className="text-left mb-2">Чтобы использовать скрипт из тНавигатора:</p>
          <ol className="list-decimal list-inside space-y-1 text-left">
            <li className="text-left">Добавьте скрипт в систему (загрузите файл или создайте новый)</li>
            <li className="text-left">Откройте скрипт и скопируйте его <strong>логический путь</strong> (например, "geology/test.py")</li>
            <li className="text-left">Вызовите скрипт удаленно через HTTP запрос из тНавигатора</li>
            <li className="text-left">Передайте данные в виде словаря, получите результат</li>
          </ol>
        </div>
      ),
      placement: 'center',
    },
    {
      target: '[data-onboarding="code-example-button"]',
      content: (
        <div className="text-left">
          <h3 className="text-lg font-semibold mb-2">Пример кода</h3>
          <p className="text-left">Нажмите на кнопку "Пример кода", чтобы увидеть готовый пример вызова скрипта из тНавигатора.</p>
          <p className="text-left mt-2">Пример показывает, как использовать встроенную библиотеку <code className="bg-gray-100 px-1 rounded">http.client</code> для выполнения скрипта на сервере.</p>
          <p className="text-left mt-2">Важно: убедитесь, что вызываемый скрипт уже создан и существует на сервере перед выполнением запроса.</p>
        </div>
      ),
      placement: 'bottom',
    },
    {
      target: '[data-onboarding="new-folder-top"]',
      content: (
        <div className="text-left">
          <h3 className="text-lg font-semibold mb-2">Создание папки</h3>
          <p className="text-left">Теперь давайте научимся использовать сервис. Начнем с создания папки для организации скриптов.</p>
        </div>
      ),
      placement: 'bottom',
    },
    {
      target: '[data-onboarding="new-script-top"]',
      content: (
        <div className="text-left">
          <h3 className="text-lg font-semibold mb-2">Создание скрипта</h3>
          <p className="text-left">Скрипт можно создать двумя способами:</p>
          <ul className="list-disc list-inside mt-2 space-y-1 text-left">
            <li className="text-left">Загрузить готовый файл</li>
            <li className="text-left">Написать код прямо в редакторе</li>
          </ul>
        </div>
      ),
      placement: 'bottom',
    },
    {
      target: 'body',
      content: (
        <div className="text-left">
          <h3 className="text-lg font-semibold mb-2">Структура скрипта</h3>
          <p className="mb-2 text-left">Важно знать требования к скриптам:</p>
          <ul className="list-disc list-inside space-y-1 mb-3 text-left">
            <li className="text-left">Скрипт должен быть в одном файле</li>
            <li className="text-left">Должна быть функция <code className="bg-gray-100 px-1 rounded">main(data: dict) -&gt; dict</code>, принимающая единственный аргумент - словарь</li>
            <li className="text-left">Могут быть другие функции, вызываемые из <code className="bg-gray-100 px-1 rounded">main</code></li>
            <li className="text-left">Входные данные отправляются в функцию <code className="bg-gray-100 px-1 rounded">main</code></li>
            <li className="text-left">Функция <code className="bg-gray-100 px-1 rounded">main</code> должна вернуть словарь любой структуры</li>
          </ul>
          <div className="bg-gray-50 p-3 rounded text-sm font-mono text-left">
            <div className="text-left">def helper_function(x):</div>
            <div className="ml-4 text-left">return x * 2</div>
            <div className="mt-2 text-left">def main(data: dict) -&gt; dict:</div>
            <div className="ml-4 text-left">value = data.get("value", 0)</div>
            <div className="ml-4 text-left">result = helper_function(value)</div>
            <div className="ml-4 text-left">return {`{"result": result}`}</div>
          </div>
        </div>
      ),
      placement: 'center',
    },
    {
      target: '[data-onboarding="execute-script"]',
      content: (
        <div className="text-left">
          <h3 className="text-lg font-semibold mb-2">Выполнение скрипта</h3>
          <p className="text-left">После создания скрипта его можно выполнить прямо здесь. Нажмите кнопку "Выполнить", чтобы открыть панель выполнения и протестировать скрипт.</p>
        </div>
      ),
      placement: 'left',
    },
    {
      target: '[data-onboarding="edit-script"]',
      content: (
        <div className="text-left">
          <h3 className="text-lg font-semibold mb-2">Редактирование скрипта</h3>
          <p className="text-left">Скрипт можно редактировать в любое время. Нажмите на кнопку редактирования, чтобы изменить код.</p>
        </div>
      ),
      placement: 'left',
    },
    {
      target: 'body',
      content: (
        <div className="text-left">
          <h3 className="text-lg font-semibold mb-2">Права доступа</h3>
          <p className="mb-2 text-left">Важная информация о правах:</p>
          <ul className="list-disc list-inside space-y-1 text-left">
            <li className="text-left"><strong>Скрипт</strong> может редактировать только его <strong>автор</strong> или <strong>администратор</strong></li>
            <li className="text-left"><strong>Папку</strong> может редактировать или удалить только её <strong>автор</strong> или <strong>администратор</strong></li>
            <li className="text-left"><strong>Создавать</strong> папки и скрипты может <strong>любой пользователь</strong></li>
          </ul>
        </div>
      ),
      placement: 'center',
    },
  ];

  const handleJoyrideCallback = useCallback(
    async (data: CallBackProps) => {
      const { status, type, index, action, step } = data;

      // Log all events for debugging
      console.log('Joyride callback:', { status, type, index, action, step: step?.target });

      // Handle completion or skip
      if (status === STATUS.FINISHED || status === STATUS.SKIPPED) {
        // Mark onboarding as completed
        try {
          await updateOnboardingStatus(false);
        } catch (error) {
          console.error('Failed to update onboarding status:', error);
        }
        onComplete();
        return;
      }

      // Handle target not found - Joyride should continue automatically
      if (type === 'error:target_not_found') {
        console.warn('Onboarding target not found for step', index, 'target:', step?.target);
        // Joyride will automatically continue to next step
      }

      // Handle step navigation - Joyride handles this automatically
      if (action === 'next' || action === 'prev') {
        console.log('Step navigation:', action, 'to index', index);
      }
    },
    [updateOnboardingStatus, onComplete]
  );

  const joyrideStyles = {
    options: {
      primaryColor: '#3b82f6', // primary color
      zIndex: 10000,
    },
    tooltip: {
      borderRadius: 8,
    },
    buttonNext: {
      backgroundColor: '#3b82f6',
      borderRadius: 6,
      padding: '8px 16px',
    },
    buttonBack: {
      color: '#6b7280',
      marginRight: 8,
    },
    buttonSkip: {
      color: '#6b7280',
    },
  };

  return (
    <Joyride
      steps={steps}
      run={run}
      continuous
      showProgress
      showSkipButton
      callback={handleJoyrideCallback}
      styles={joyrideStyles}
      locale={{
        back: 'Назад',
        close: 'Закрыть',
        last: 'Завершить',
        next: 'Далее',
        skip: 'Пропустить',
      }}
      floaterProps={{
        disableAnimation: true,
      }}
      disableScrollParentFix={false}
      disableOverlayClose={false}
      spotlightClicks={false}
    />
  );
};

export default Onboarding;


#ifndef PIN_HPP
#define PIN_HPP

#include <string>
#include <thread>
#include <atomic>
#include <mutex>
#include <stdexcept>

/**
 * @enum PinMode
 * @brief Define os modos de operação de um pino GPIO.
 */
enum PinMode
{
    DIGITAL_IN,  ///< Entrada digital
    DIGITAL_OUT, ///< Saída digital
    PWM          ///< Saída PWM (hardware ou software)
};

/**
 * @class Pin
 * @brief Abstração de baixo nível para controle de pinos GPIO na Raspberry Pi.
 *
 * Suporta:
 *   - Leitura/escrita digital
 *   - PWM por hardware (pinos 12, 13, 18, 19) via sysfs pwmchip0
 *   - PWM por software (qualquer pino DIGITAL_OUT) via thread dedicada
 *
 * Numeração: BCM (Broadcom), valores válidos: 0–27.
 */
class Pin
{
public:
    /**
     * @brief Constrói e inicializa o pino.
     * @param pin    Número BCM do pino (0–27).
     * @param mode   Modo de operação (DIGITAL_IN, DIGITAL_OUT ou PWM).
     * @throws std::runtime_error se o pino for inválido, não suportar PWM
     *         quando solicitado, ou se o sysfs não puder ser acessado.
     */
    Pin(int pin, PinMode mode);

    /**
     * @brief Destrói o objeto e libera o pino automaticamente.
     */
    ~Pin();

    // Impede cópia — um pino não deve ter dois donos
    Pin(const Pin&)            = delete;
    Pin& operator=(const Pin&) = delete;

    /**
     * @brief Libera o pino do sysfs e encerra threads ativas.
     *
     * Seguro para chamar mais de uma vez; chamadas subsequentes são no-ops.
     */
    void release();

    // ------------------------------------------------------------------ //
    //  Interface Digital                                                  //
    // ------------------------------------------------------------------ //

    /**
     * @brief Escreve um valor digital no pino.
     * @param value  0 (LOW) ou 1 (HIGH).
     * @throws std::runtime_error se o pino não estiver no modo DIGITAL_OUT.
     */
    void write(int value);

    /**
     * @brief Lê o valor digital do pino.
     * @return 0 ou 1.
     * @throws std::runtime_error se o pino não estiver no modo DIGITAL_IN.
     */
    int read();

    // ------------------------------------------------------------------ //
    //  Interface PWM                                                      //
    // ------------------------------------------------------------------ //

    /**
     * @brief Configura e inicia o sinal PWM.
     *
     * Para pinos PWM de hardware (12, 13, 18, 19) usa o subsistema
     * pwmchip0 do kernel. Para os demais pinos (modo DIGITAL_OUT),
     * usa PWM por software em thread separada.
     *
     * @param duty       Ciclo de trabalho, entre 0.0 (0 %) e 1.0 (100 %).
     * @param frequencyHz Frequência em Hz (padrão: 50 Hz — servos/ESCs).
     *                   Para PWM de hardware, o período é derivado deste valor.
     *                   Para PWM de software, define o período da thread.
     * @throws std::runtime_error se o pino não for PWM ou DIGITAL_OUT,
     *         ou se os parâmetros estiverem fora do intervalo permitido.
     */
    void pwmWrite(float duty, float frequencyHz = 50.0f);

    /**
     * @brief Para o sinal PWM sem liberar o pino.
     *
     * Em hardware PWM: desabilita o canal (enable = 0).
     * Em software PWM: encerra a thread e coloca o pino em LOW.
     */
    void pwmStop();

    /**
     * @brief Retorna o duty cycle atual configurado.
     */
    float getDuty() const;

    /**
     * @brief Retorna a frequência atual em Hz.
     */
    float getFrequency() const;

    /**
     * @brief Retorna o modo de operação do pino.
     */
    PinMode getMode() const;

    /**
     * @brief Retorna o número BCM do pino.
     */
    int getPinNumber() const;

    /**
     * @brief Indica se o pino está ativo (inicializado e não liberado).
     */
    bool isActive() const;

private:
    // ------------------------------------------------------------------ //
    //  Estado interno                                                     //
    // ------------------------------------------------------------------ //

    int     pinNumber  = -1;
    int     kernelPin  = -1;
    int     pwmChannel = -1;
    PinMode mode;
    bool    active     = false;

    std::string gpioPath;
    std::string pwmPath;

    // Frequência e duty armazenados para consulta e reconfiguração
    std::atomic<float> currentDuty     {0.0f};
    std::atomic<float> currentFrequency{50.0f};

    // Mutex para operações de escrita/leitura em modo digital
    mutable std::mutex ioMutex;

    // ------------------------------------------------------------------ //
    //  Soft-PWM                                                          //
    // ------------------------------------------------------------------ //

    std::thread       softPwmThread;
    std::atomic<bool> runSoftPwm{false};

    /** Loop executado pela thread de software PWM. */
    void softPwmWorker();

    /** Inicia a thread de software PWM (chama apenas uma vez por sessão). */
    void startSoftPwm();

    /** Para e junta a thread de software PWM. */
    void stopSoftPwm();

    // ------------------------------------------------------------------ //
    //  Utilitários                                                        //
    // ------------------------------------------------------------------ //

    static int  bcmToKernel(int bcm);
    static bool pathExists(const std::string& path);
    static void validatePin(int pin);
    static bool isPWMPin(int pin);
    static int  gpioToPWMChannel(int pin);

    void        writeFile(const std::string& path, const std::string& value);
    std::string readFile(const std::string& path);
};

#endif // PIN_HPP

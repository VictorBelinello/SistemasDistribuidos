### Conection constants 
PORT = 3000 # multicast port

#### Constantes relativas ao header da mensagem
# Header:   UUID | Porta unicast | Tipo mensagem | Tamanho mensagem | 
# UUID
UUID_SHORT = 4 # The uuid used here is a short version of the original that has 32bytes
UUID_RANGE = slice(0,UUID_SHORT) 
# Porta unicast
PORT_RANGE = slice(UUID_RANGE.stop, UUID_RANGE.stop + 5) # 5 caracteres logo apos UUID

# Tipo mensagem
MSG_TYPE_RANGE = slice(PORT_RANGE.stop , PORT_RANGE.stop + 1) # Tipo da mensagem tem 1 char apenas 
MSG_TYPE_PUBKEY = "0"
MSG_TYPE_REPUTATION = "1"
MSG_TYPE_NORMAL = "2"
MSG_TYPE_REPORT = "3"
MSG_TYPE_EXIT = "4"

# Tamanho mensagem
import math
MSG_MAX_CHAR = 10000 # Numero maximo de caracteres da mensagem
MAX_NUMBER_DIGITS_MSG = int(math.log10(MSG_MAX_CHAR)) + 1  # Numero de char/digitos necessarios para representar o tamanho da mensagem. Exemplo: Se a mensagem tiver 2487 caracteres, para representar tal tamanho precisamos de 4 caracteres ('2','4','8','7')
MSG_SIZE_RANGE = slice(MSG_TYPE_RANGE.stop, MSG_TYPE_RANGE.stop + MAX_NUMBER_DIGITS_MSG) 

# Inicio da mensagem em si
MSG_START_BYTE = MSG_SIZE_RANGE.stop
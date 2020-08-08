import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.UnsupportedEncodingException;
import java.nio.ByteBuffer;
import java.util.Arrays;
import java.util.UUID;

public class Header {
    public UUID uuid;
    public char type;
    public int startOfSignature;

    static final int HEADER_SIZE = 41; // Header com tamanho fixo de 41bytes

    public Header(UUID uuid, char type, int startOfSignature) {
        // String header = msg.substring(0, HEADER_SIZE); // 40 primeiros bytes = header
        // UUID uuid = UUID.fromString(header.substring(0, 36)); // Bytes [0,35] = UUID
        // char typeOfMessage = header.charAt(36); // Byte 36 = tipo de mensagem sendo enviada
        // int startOfSignature = header.substring(37, HEADER_SIZE);

        this.uuid = uuid;
        this.type = type;
        this.startOfSignature = startOfSignature;

    }

    public Header(UUID uuid, char type) {
        this(uuid, type, 0);
    }

    public byte[] appendHeaderTo(byte[] msg) throws IOException {
        ByteArrayOutputStream os = new ByteArrayOutputStream();
        ByteBuffer bb = ByteBuffer.allocate(4);
        bb.putInt(this.startOfSignature);

        os.write(this.uuid.toString().getBytes());
        os.write((byte) this.type);
        os.write(bb.array());
        os.write(msg);

        return os.toByteArray();
    }

    public byte[] appendHeaderTo(String msg) throws IOException {
        return this.appendHeaderTo(msg.getBytes());
    }

    public static Header extractHeader(byte[] msg) throws UnsupportedEncodingException {
        byte[] rawID = Arrays.copyOfRange(msg, 0, 36);
        byte rawType = msg[36];
        byte[] rawStartOfSignature = Arrays.copyOfRange(msg, 37, 37 + 4);

        String stringID = new String(rawID, "UTF8");
        UUID uuid = UUID.fromString(stringID);

        char type = (char) rawType;

        ByteBuffer bb = ByteBuffer.wrap(rawStartOfSignature);
        int startOfSignature = bb.getInt();

        Header h = new Header(uuid, type, startOfSignature);
        return h;
    }

    public String toString() {
        return String.format("UUID:%s\n|Type of message:%c\n|Start:%d\n", this.uuid.toString(), this.type,
                this.startOfSignature);
    }
}
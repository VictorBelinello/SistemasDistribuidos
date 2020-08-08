import java.io.IOException;
import java.net.InetAddress;
import java.net.SocketException;
import java.net.UnknownHostException;
import java.security.InvalidKeyException;
import java.security.NoSuchAlgorithmException;
import java.security.SignatureException;
import java.util.UUID;

public class Main {
    public static void main(String args[]) {
        try {
            InetAddress group = InetAddress.getByName(args[0]);
            MulticastPeer peer = new MulticastPeer();

            // Salva o IP do grupo multicast
            peer.setGroup(group);

            // Inicializa assinatura (cria as chaves publica e privada)
            peer.initSignature();
            
            // Obtem um identificador unico
            peer.setUUID(UUID.randomUUID());

            // Entra no grupo multicast (envia chave publica)
            peer.joinMulticastGroup();

            // Inicia thread de leitura de mensagens (metodo run)
            peer.start();

        } catch (UnknownHostException e) {
            System.out.print(e);
        } catch (SocketException e) {
            System.out.println("Socket: " + e.getMessage());
        } catch (IOException e) {
            System.out.println("IO: " + e.getMessage());
        } catch (SignatureException e) {
            System.out.println("Signature: " + e.getMessage());
        } catch (InvalidKeyException e) {
            System.out.println("InvalidKey: " + e.getMessage());
        } catch (NoSuchAlgorithmException e) {
            System.out.println("NoSuchAlgorithm: " + e.getMessage());
        }

    }
}
import java.net.InetAddress;
import java.net.UnknownHostException;

public class Main{
    public static void main(String args[]) {
        try{
            InetAddress group = InetAddress.getByName(args[0]);
            MulticastPeer peer = new MulticastPeer(group);
        } catch(UnknownHostException e){
            System.out.print(e);
        }
        
        
    }
}
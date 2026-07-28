package socket;

import java.io.IOException;
import java.net.ServerSocket;
import java.util.ArrayList;
import java.net.Socket;
import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.io.File;
import java.io.InputStream;
import java.io.OutputStream;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.FileWriter;
import java.io.ByteArrayOutputStream;
import java.io.Writer;

import java.net.*;
import java.nio.ByteBuffer;
import java.nio.channels.*;
import java.nio.charset.StandardCharsets;
import java.util.*;

public class socketforapp {
   private static final String ROUTE_PLAN_PATH = "output/routePlan.txt";

   // 監聽位址／埠：args[0] args[1] > 環境變數 > 預設值（0.0.0.0 表示所有介面）
   private static String resolveHost(String[] args) {
      if (args.length >= 1) return args[0];
      String env = System.getenv("ROUTE_SERVER_HOST");
      return (env == null || env.isEmpty()) ? "0.0.0.0" : env;
   }

   private static int resolvePort(String[] args) {
      if (args.length >= 2) return Integer.parseInt(args[1]);
      String env = System.getenv("ROUTE_SERVER_PORT");
      return (env == null || env.isEmpty()) ? 7000 : Integer.parseInt(env);
   }

   // 從累積緩衝切出所有完整的一行；沒收完的殘段留在 buffer 裡等下一次讀取。
   // 只解碼完整的一行，多位元組中文字被切在兩個封包之間也不會壞掉。
   static List<String> extractLines(ByteArrayOutputStream buffer, byte[] data, int length) throws IOException {
      List<String> lines = new ArrayList<String>();
      if (length > 0) buffer.write(data, 0, length);
      byte[] pending = buffer.toByteArray();
      int start = 0;
      for (int i = 0; i < pending.length; i++) {
         if (pending[i] != '\n') continue;
         String line = new String(pending, start, i - start, StandardCharsets.UTF_8).trim();
         start = i + 1;
         if (line.length() > 0) lines.add(line);
      } // for
      buffer.reset();
      if (start < pending.length) buffer.write(pending, start, pending.length - start);
      return lines;
   }

   // 明定 UTF-8，與 Python 端 read_txt.py 的 encoding="utf-8" 一致（平台預設在 Windows 是 MS950）
   private static void appendRoutePlan(String line) throws IOException {
      Writer fr = new OutputStreamWriter(new FileOutputStream(ROUTE_PLAN_PATH, true), StandardCharsets.UTF_8);
      try {
         fr.write(line + "\n");
         fr.flush();
      } finally {
         fr.close();
      }
   }

   public static void main(String[] args) throws Exception {
      new File("output").mkdirs();
      InetAddress host = InetAddress.getByName(resolveHost(args));
      int port = resolvePort(args);
      Selector selector = Selector.open();
      ServerSocketChannel serverSocketChannel = ServerSocketChannel.open();
      serverSocketChannel.configureBlocking(false);
      serverSocketChannel.bind(new InetSocketAddress(host, port));
      serverSocketChannel.register(selector, SelectionKey.OP_ACCEPT);
      SelectionKey key = null;

      System.out.println("Server already opens on " + host.getHostAddress() + ":" + port);
      while (true) {
    	 System.out.println("Keep Opening");
         if (selector.select() <= 0)
            continue;
         
         Set<SelectionKey> selectedKeys = selector.selectedKeys();
         Iterator<SelectionKey> iterator = selectedKeys.iterator();

         while (iterator.hasNext()) {
        	System.out.println("New client");
            key = (SelectionKey) iterator.next();
            iterator.remove();
            if (key.isAcceptable()) {
               SocketChannel sc = serverSocketChannel.accept();
               sc.configureBlocking(false);
               // 每條連線各自帶一個累積緩衝，TCP 可能把一筆記錄拆開或把兩筆黏在一起
               sc.register(selector, SelectionKey.OP_READ, new ByteArrayOutputStream());
               System.out.println("Connection Accepted: " + sc.getLocalAddress() + "n");
            } // if

            if (key.isReadable()) {
               SocketChannel sc = (SocketChannel) key.channel();
               ByteArrayOutputStream buffer = (ByteArrayOutputStream) key.attachment();
               ByteBuffer bb = ByteBuffer.allocate(1024);
               int readCount = sc.read(bb);
               if (readCount < 0) {
                  sc.close();
                  System.out.println( "Connection closed..." );
                  System.out.println( "Server will keep running. " +
                     "Try running another client to " +
                     "re-establish connection");
               } // if
               else if (readCount > 0) {
                  for (String result : extractLines(buffer, bb.array(), readCount)) {
                     System.out.println("Message received: " + result + " Message length= " + result.length());
                     appendRoutePlan(result);
                  } // for
               } // else if
            }
         }
      }
   }
}
/*
public class socketforapp {

    private static int serverport = 12133;     //自訂的 Port
    private static ServerSocket serverSocket; //伺服端的Socket
    private static int count=0; //計算有幾個 Client 端連線
    private static FileWriter fr;
 
    // 用 ArrayList 來儲存每個 Client 端連線
    private static ArrayList clients = new ArrayList();
 
    public static void main(String[] args) {   
        try {
            serverSocket = new ServerSocket(serverport);
            System.out.println("Server is start.");
            // 顯示等待客戶端連接
            System.out.println("Waiting for client connect");
            // 當Server運作中時
            fr = new FileWriter("Test123.txt");

            while (!serverSocket.isClosed()) { 
                // 呼叫等待接受客戶端連接
                waitNewClient();
            }
            
            fr.close();
        } catch (IOException e) {
            System.out.println("Server Socket ERROR");
        }
        
    }
 
    // 等待接受 Client 端連接
    public static void waitNewClient() {
        try {
            Socket socket = serverSocket.accept();
            ++count;
            System.out.println("現在使用者個數："+count);
 
            // 呼叫加入新的 Client 端
            addNewClient(socket);
            
        } catch (IOException e) {}
    }
 
    // 加入新的 Client 端
    public static void addNewClient(final Socket socket) throws IOException {
        // 以新的執行緒來執行
        Thread t = new Thread(new Runnable() {
            @Override
            public void run() {
                try {
                    // 增加新的 Client 端
                    clients.add(socket);
                    // 取得網路串流 
                    BufferedReader br = new BufferedReader(new InputStreamReader(socket.getInputStream()));      
                    // 當Socket已連接時連續執行
                    while (socket.isConnected()) {
                        // 取得網路串流的訊息
                        String msg= br.readLine();
                        if(msg==null){
                         System.out.println("Client Disconnected!");
                         break;
                        }
                        //輸出訊息
                        fr.write(msg + "\n");
                        fr.flush();
                        System.out.println(msg);
                        // 廣播訊息給其它的客戶端
                        castMsg(msg);
                    }
                } catch (IOException e) {
                 e.getStackTrace();
                }
                finally{
                   // 移除客戶端
                   clients.remove(socket);
                   --count;
                   System.out.println("現在使用者個數："+count);
                }
            }
        });
 
        // 啟動執行緒
        t.start();
    }
 
    // 廣播訊息給其它的客戶端
    public static void castMsg(String Msg){
        // 創造socket陣列
        Socket[] clientArrays =new Socket[clients.size()]; 
        // 將 clients 轉換成陣列存入 clientArrays
        clients.toArray(clientArrays);
        // 走訪 clientArrays 中的每一個元素
        for ( Socket socket : clientArrays ) {
            try {
                // 創造網路輸出串流
                BufferedWriter bw;
                bw = new BufferedWriter( new OutputStreamWriter(socket.getOutputStream()));
                // 寫入訊息到串流
                bw.write(Msg+"\n");
                // 立即發送
                bw.flush();
            } catch (IOException e) {}
        }
    }
	
}
*/
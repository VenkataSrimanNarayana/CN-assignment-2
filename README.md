# Question 1

**(a)** The network topology called `NetworkTopo()` has been defined inside the q1.py file using the python api of mininet. `pingall` command inside mininet give the following output.  
 ![Alt text](images/image.png)  
**(b)** Running the wireshark on router `ra` using the command `ra wireshark &`, and then running the `pingall` command inside mininet captures the following packets. The entire TCP Dump has been captured and saved inside the file called `q1_packets.pcapng`.
![Alt text](images/image1.png)  
**(c)** Updated the routing table in both ra and rc so that the packets are only sent to the rb, where they are again forwarded.

> Comparing latency using the ping command and iperf tool gave the following
>
> 1. For path h1 -> ra -> rc -> h6  
>    ![Alt text](images/image2.png)  
>    ![Alt text](images/image6.png)
> 2. For the path h1 -> ra -> rb -> rc -> h6  
>    ![Alt text](images/image3.png)  
>    ![Alt text](images/image7.png)
>
> It can be observed that the latency is less for the path h1 -> ra -> rb -> rc -> h6 from both ping's `avg time` and `irtt` in iperf tool.

**(d)** The routing tables are printed using the code. The routing tables are in order ra, rb, rc.

> For (a),  
> ![Alt text](images/image4.png)  
> For (c),  
> ![Alt text](images/image5.png)  
> The routing tables have also been saved to the files `q1_routes_a.txt` and `q1_routes_c.txt` for the respective questions (a) and (c)

# Question 2

**(a)** The network topology given in the image is defined in `NetworkTopo()` class, and the class takes the link*loss parameter, which sets the value of the \_s1-s2* link packet loss percentage. The file `q2.py` can be run using python with `sudo` permissions. The file can be run using the below command. Where the values of config(required) can be `b` (or) `c`, values of congestion control(not required) can be any one of `{Vegas, Cubic, Reno, BBR}`, and values of link loss(not required) can be any integer between `0` and `100`

```console
python q2.py --config[-c] <config> --link-loss[-ll] <link loss> --congestion-control[-cc] <congestion control>
```

> **_Note:_**
>
> 1. If no `congestion-control` option is given for config `b` then the program plots Throughput for all values of all the above given congestion control mechanism, for the client `h1`.
> 2. If a `congestion-control` option is given for config `c` then the program plots Throughput for all hosts `h1`, `h2`, and `h3`, for the given value of congestion control in the same graph. If it is not given then it plots Throughput for all values of the congestion control mechanism for each given host {`h1`, `h2`, `h3`} in a different graph.
> 3. If no `link-loss` option is mentioned then the throughput analysis is done using `0` link loss for `s1-s2` link.
> 4. The program does not enter into `mininet` CLI.

**(b)** The client is run for `10sec` and the plots are obtained by running the file using the below command.

```console
sudo python q2.py --config b
```

![Alt text](images/q2_b_all_cc_0.png)

It can be observed that BBR congestion control gives less throughput, vegas shows a steady throughput after some time. Cubic, and Reno congestion control shows a decreasing throughput after some time, and cubic also increases after the decrease. Reno and BBR have slow start, whereas Vegas and Cubic have fast start.

**(c)** The following commands were used to get the throughput plots for different hosts using the mentioned congestion control algorithm.

> **_Note:_** File when run at different times might produce different plots depending on which host first starts sending packets.

```console
sudo python q2.py --config c -cc BBR
```

![Alt text](images/q2_c_bbr.png)

```console
sudo python q2.py --config c -cc Cubic
```

![Alt text](images/q2_c_cubic.png)

```console
sudo python q2.py --config c -cc Reno
```

![Alt text](images/q2_c_reno.png)

```console
sudo python q2.py --config c -cc Vegas
```

![Alt text](images/q2_c_vegas.png)

It can be observed that BBR congestion control gives less throughput, vegas appears to be fair for different hosts. BBR, and Reno congestion control show frequent changes. In case of BBR, it appears that all the hosts sharing the bandwidth respond similarly to the congestion control algorithm. Vegas appears to be the first to start fair sharing of bandwidth among the hosts, and it does not to show frequent changes in throughput if the network conditions are not changed. This may be because of the fact that Vegas uses RTT to throttle bandwith usage, and it does not use packet loss as a metric. Cubic and Reno use packet loss as a metric to throttle the andwidth usage, and hence they show frequent changes in throughput.

From questions (b) and (c) it can be observed that both network conditions and congestion control algorithm affect the throughput.

The following command was used to get the throughput plots for different congestion control algorithm for a given host.

```console
sudo python q2.py --config c
```

![Alt text](images/q2_c_h1.png)
![Alt text](images/q2_c_h2.png)
![Alt text](images/q2_c_h3.png)

**(d)** The following command was used to get the throughput plots on client side for different congestion control algorithm for a given link loss{`1`, `3`}.

```console
sudo python q2.py --config b -ll 1
```

![Alt text](images/q2_b_all_cc_1.png)

```console
sudo python q2.py --config b -ll 3
```

![Alt text](images/q2_b_all_cc_3.png)

It appears that BBR shows the highest throughput in case of packets losses and very high fluctuations in throughput during loss as compared to others. Vegas shows very less throughput change. This might be becuase of the fact that vegas uses RTT to throttle bandwith usage, and it does not use packet loss as a metric. From this we can say that BBR causes more congestion in the network as compared to others(which are sensitive to congestion in the network).

### References:

1. [Iperf](https://iperf.fr/)
2. [Mininet](http://mininet.org/)
3. [Mininet Python API](http://mininet.org/api/annotated.html)
4. [Mininet Router Implementation](https://github.com/mininet/mininet/blob/master/examples/linuxrouter.py)  
   5 .[Congestion Control Algorithms](https://www.speedguide.net/articles/tcp-congestion-control-algorithms-comparison-7423)

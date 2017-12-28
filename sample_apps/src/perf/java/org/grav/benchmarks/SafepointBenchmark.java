package org.grav.benchmarks;

import org.openjdk.jmh.annotations.Benchmark;
import org.openjdk.jmh.annotations.CompilerControl;

import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

public class SafepointBenchmark
{
    @Benchmark
    public void findTheSafepoint()
    {
        int sum = 0;
        for (int i = 0; i < Integer.MAX_VALUE; i++)
        {
            sum += i;
        }
        cheapMethod(sum);
    }

    @CompilerControl(CompilerControl.Mode.DONT_INLINE)
    private void cheapMethod(final int sum)
    {
        if (sum != 1073741825) {
            throw new IllegalStateException();
        }
    }



    // run with -XX:+PrintSafepointStatistics
    public static void main(final String[] args) throws Exception
    {
        final SafepointBenchmark benchmark = new SafepointBenchmark();
//        final ExecutorService es = Executors.newFixedThreadPool(10);
//        for(int i = 0; i < 10; i++)
//        {
//            es.execute(() -> {
                for (int j = 0; j < 10000; j++)
                {
                    benchmark.findTheSafepoint();

                }

//            });
//        }
//        es.shutdown();
//        es.awaitTermination(10, TimeUnit.MINUTES);
    }
}
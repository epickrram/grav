package org.grav.sample_apps;


import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.HashMap;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.TreeSet;
import java.util.stream.Collectors;

public class WordCountApp
{

    private static final String DEFAULT_FILE = "hamlet.txt";

    public static void main(final String[] args) throws Exception
    {
        String file = DEFAULT_FILE;
        if (args.length >= 1)
        {
            file = args[0];
        }

        while (true)
        {
            final String content = new String(
                Files.readAllBytes(Paths.get(ClassLoader.getSystemResource(file).toURI())));
            final Map<String, Integer> wordCountByWordMap = new HashMap<>();
            for (final String word : new BruteForce().words(content))
            {
                wordCountByWordMap.compute(word, (key, count) -> (count == null) ? 1 : count + 1);
            }

            wordCountByWordMap.entrySet().stream().
                map(entry -> new WordCount(entry.getKey(), entry.getValue())).
                collect(Collectors.toCollection(TreeSet::new)).
                forEach(System.out::println);
        }
    }

    private static class BruteForce
    {

        private Iterable<String> words(final String text)
        {
            final List<String> words = new LinkedList<>();

            int i = text.length();
            int lastChar = -1;

            while (--i != -1)
            {
                if (lastChar == -1 && !isSeparator(text.charAt(i)))
                {
                    lastChar = i;
                } else if (lastChar != -1)
                {
                    if (isSeparator(text.charAt(i)))
                    {
                        words.add(0, text.substring(i + 1, lastChar + 1));
                        lastChar = -1;
                    }
                }
            }
            if (lastChar != -1)
            {
                words.add(0, text.substring(0, lastChar + 1));
            }

            return words;
        }

        private boolean isSeparator(final char c)
        {
            return !Character.isLetterOrDigit(c);
        }
    }

    private static class WordCount implements Comparable<WordCount>
    {
        private final String word;
        private final int count;

        public WordCount(final String word, final int count)
        {
            this.word = word;
            this.count = count;
        }

        @Override
        public int compareTo(final WordCount o)
        {
            final int diff = count - o.count;
            return (diff == 0) ? word.compareTo(o.word) : diff;
        }

        @Override
        public boolean equals(final Object o)
        {
            if (this == o)
            {
                return true;
            }
            if (o == null || getClass() != o.getClass())
            {
                return false;
            }
            final WordCount wordCount = (WordCount) o;
            return count == wordCount.count &&
                Objects.equals(word, wordCount.word);
        }

        @Override
        public int hashCode()
        {
            return Objects.hash(word, count);
        }

        @Override
        public String toString()
        {
            return count + " - " + word;
        }
    }
}

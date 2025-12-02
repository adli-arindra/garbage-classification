using Microsoft.ML;
using Microsoft.ML.Data;

namespace test
{
    public class ModelInput
    {
        [ColumnName("input")]
        [VectorType(3, 224, 224)]
        public float[] Data { get; set; }
    }

    public class ModelOutput
    {
        [ColumnName("output")]
        public float[] Predictions { get; set; }
    }

    public class ImagePath
    {
        public string Path { get; set; }
    }

    internal class Program
    {
        static float[] Softmax(float[] logits)
        {
            float max = logits.Max();
            float sum = 0f;
            var exp = new float[logits.Length];

            for (int i = 0; i < logits.Length; i++)
            {
                exp[i] = (float)Math.Exp(logits[i] - max);
                sum += exp[i];
            }

            for (int i = 0; i < logits.Length; i++)
                exp[i] /= sum;

            return exp;
        }

        static void Main(string[] args)
        {
            Console.Write("Image path: ");
            var path = Console.ReadLine();

            if (string.IsNullOrWhiteSpace(path) || !File.Exists(path))
            {
                Console.WriteLine("File not found.");
                return;
            }

            string[] classNames = new[]
            {
                "battery",
                "biological",
                "cardboard",
                "clothes",
                "glass",
                "leafs",
                "metal",
                "paper",
                "plastic_bag",
                "plastic_bottle",
            };

            try
            {
                var ml = new MLContext();

                var pipeline = ml.Transforms.LoadImages(
                        outputColumnName: "img",
                        imageFolder: "",
                        inputColumnName: nameof(ImagePath.Path))
                    .Append(ml.Transforms.ResizeImages(
                        "img_resized", 224, 224, "img"))
                    .Append(ml.Transforms.ExtractPixels(
                        "input", "img_resized"))
                    .Append(ml.Transforms.ApplyOnnxModel(
                        modelFile: "model.onnx",
                        inputColumnNames: new[] { "input" },
                        outputColumnNames: new[] { "output" }));

                var emptyData = ml.Data.LoadFromEnumerable(new List<ImagePath>());
                var model = pipeline.Fit(emptyData);

                var engine = ml.Model.CreatePredictionEngine<ImagePath, ModelOutput>(model);

                var result = engine.Predict(new ImagePath { Path = path });

                var raw = result.Predictions;
                var probs = Softmax(raw);

                Console.WriteLine("Probabilities:");
                for (int i = 0; i < probs.Length; i++)
                {
                    var label = i < classNames.Length ? classNames[i] : $"class_{i}";
                    Console.WriteLine($"{label}: {probs[i]}");
                }

            }
            catch (Exception ex)
            {
                Console.WriteLine("Error:");
                Console.WriteLine(ex.Message);
            }
        }
    }
}

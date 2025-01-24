from models.tasks.Task import Task


class ExtractTextFromElementTask(Task):

    async def execute(self):
        try:
            # Set the task status to "RUNNING" to indicate that execution has started.
            await self.setStatus("RUNNING")

            # Select the HTML element using the provided selector.
            element = self.inputs["html"].select_one(self.inputs["selector"])
           
            if element is None:
                # If the element does not exist, set the output with an appropriate message.
                await self.setOutputs({"extractedText": "Your mistake: Element does not exist :("})
                # Mark the task as "COMPLETED" since processing is finished.
                await self.setStatus("COMPLETED")
                return self.outputs
            
            # Extract text content from the element, stripping unnecessary whitespace.
            element_text = element.getText(strip=True)
         
            # Set the extracted text as the output.
            await self.setOutputs({"extractedText": element_text})

            # Mark the task as "COMPLETED" successfully.
            await self.setStatus("COMPLETED")
            
            return self.outputs
        except Exception as e:
            await self.setStatus("FAILED")
            raise ValueError(e)
           